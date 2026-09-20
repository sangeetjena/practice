"""CronJob controller: create one bounded FlinkDeployment, then wait for its actual result."""

import copy
import json
import os
import re
import ssl
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def build_run(template, start, end, run_id=None):
    begin, finish = datetime.strptime(start, "%Y-%m-%d").date(), datetime.strptime(end, "%Y-%m-%d").date()
    if not begin < finish or (finish - begin).days > 366:
        raise ValueError("Bounded runs require a positive interval of at most 366 days")
    if run_id is not None and not re.fullmatch(r"[a-z][a-z0-9-]{2,23}", run_id):
        raise ValueError("run_id must contain 3-24 lowercase letters/digits/hyphens")
    manifest = copy.deepcopy(template)
    name = "join-batch-" + (run_id or start.replace("-", ""))
    manifest["metadata"]["name"] = name
    manifest["metadata"]["labels"]["run-date"] = start
    manifest["spec"]["job"]["upgradeMode"] = "stateless"
    arguments = manifest["spec"]["job"]["args"]
    arguments[arguments.index("--continuous") + 1] = "false"
    output_index = arguments.index("--output-uri") + 1
    arguments[output_index] = arguments[output_index].rstrip("/") + "/batch/" + name
    arguments.extend(["--start-date", start, "--end-date", end])
    configuration = manifest["spec"]["flinkConfiguration"]
    for key in ("state.checkpoints.dir", "state.savepoints.dir", "high-availability.storageDir"):
        configuration[key] = configuration[key].rstrip("/") + "/" + name
    return manifest


def main():
    namespace = os.environ["NAMESPACE"]
    today = datetime.now(UTC).date()
    start = os.environ.get("START_DATE", (today - timedelta(days=1)).isoformat())
    end = os.environ.get("END_DATE", today.isoformat())
    if not datetime.fromisoformat(start) < datetime.fromisoformat(end):
        raise ValueError("Invalid batch interval")
    template = json.loads(Path("/config/template.json").read_text())
    manifest = build_run(template, start, end)
    host = os.environ["KUBERNETES_SERVICE_HOST"]
    port = os.environ.get("KUBERNETES_SERVICE_PORT_HTTPS", "443")
    account = Path("/var/run/secrets/kubernetes.io/serviceaccount")
    context = ssl.create_default_context(cafile=str(account / "ca.crt"))
    base = f"https://{host}:{port}/apis/flink.apache.org/v1beta1/namespaces/{namespace}/flinkdeployments"

    def request(method, url, body=None):
        # Re-read the projected token so polling also works after token rotation.
        token = (account / "token").read_text().strip()
        req = Request(
            url,
            method=method,
            data=json.dumps(body).encode() if body else None,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        with urlopen(req, context=context, timeout=60) as response:
            return json.load(response)

    try:
        request("POST", base, manifest)
    except HTTPError as error:
        if error.code != 409:
            raise
        existing = request("GET", base + "/" + manifest["metadata"]["name"])
        if (
            existing["spec"]["image"] != manifest["spec"]["image"]
            or existing["spec"]["job"]["args"] != manifest["spec"]["job"]["args"]
        ):
            raise RuntimeError(
                "Existing daily batch has a different release/window; use an explicit ad hoc name"
            ) from None
    deadline = time.monotonic() + int(os.environ.get("TIMEOUT_SECONDS", "14400"))
    while time.monotonic() < deadline:
        status = request("GET", base + "/" + manifest["metadata"]["name"]).get("status", {})
        state = status.get("jobStatus", {}).get("state")
        print(json.dumps({"job": manifest["metadata"]["name"], "state": state}), flush=True)
        if state == "FINISHED":
            return
        if state in {"FAILED", "CANCELED"} or status.get("error"):
            raise RuntimeError("Flink batch failed; inspect the FlinkDeployment status and logs")
        time.sleep(30)
    # Suspend the bounded job on timeout; retain its CR and output for investigation.
    resource = request("GET", base + "/" + manifest["metadata"]["name"])
    resource["spec"]["job"]["state"] = "suspended"
    request("PUT", base + "/" + manifest["metadata"]["name"], resource)
    raise RuntimeError("Flink batch timeout; suspension requested")


if __name__ == "__main__":
    main()
