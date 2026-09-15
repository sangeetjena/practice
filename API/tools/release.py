"""Bazel release entry point and developer/support commands (standard library only)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import uuid

SERVICES = ("orders", "customers", "products")
DEPLOYMENTS = (*SERVICES, "import-worker", "gateway")
DIGEST = re.compile(r"^[a-z0-9][a-z0-9./:_-]*@sha256:[0-9a-f]{64}$")


def run(*args, capture=False, **kwargs):
    result = subprocess.run(list(args), check=True, text=True,
                            stdout=subprocess.PIPE if capture else None, **kwargs)
    return result.stdout.strip() if capture else None


def workspace():
    root = os.getenv("BUILD_WORKSPACE_DIRECTORY")
    return Path(root) / "API" if root else Path(__file__).resolve().parents[1]


def resolve_bundle(value):
    if Path(value).is_file():
        return Path(value).resolve()
    from python.runfiles import runfiles
    resolved = runfiles.Create().Rlocation(value)
    if not resolved or not Path(resolved).is_file():
        raise ValueError("Release bundle missing; use bazel run //API:image or //API:deploy")
    return Path(resolved)


def unpack(bundle, destination):
    with tarfile.open(bundle) as archive:
        for member in archive:
            path = Path(member.name)
            if not member.isfile() or path.is_absolute() or ".." in path.parts:
                raise ValueError("Release archive contains an unsafe member")
            target = destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())


def build(args):
    if not args.bundle:
        raise ValueError("Build through bazel run //API:image or //API:deploy")
    bundle = resolve_bundle(args.bundle)
    revision = os.getenv("GITHUB_SHA", "local")
    with tempfile.TemporaryDirectory(prefix="api-build-") as directory:
        context = Path(directory)
        unpack(bundle, context)
        run("docker", "build", "--platform", args.platform, "--pull",
            "--build-arg", "PYTHON_BASE=" + args.python_base,
            "--build-arg", "REVISION=" + revision,
            "-f", str(context / "Dockerfile.release"), "-t", args.image, str(context))
    image_id = run("docker", "image", "inspect", args.image,
                   "--format", "{{.Id}}", capture=True)
    output = workspace() / "dist"
    output.mkdir(exist_ok=True)
    (output / "release.json").write_text(json.dumps({
        "image": args.image, "image_id": image_id, "revision": revision,
        "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
        "platform": args.platform,
    }, indent=2) + "\n")
    print("Built and unit-tested " + args.image)


def compose(args, *commands):
    root = workspace()
    host = os.getenv("DOCKER_HOST") or run(
        "docker", "context", "inspect", "--format", "{{.Endpoints.docker.Host}}", capture=True)
    if not host.startswith(("unix://", "npipe://", "tcp://127.0.0.1:", "tcp://localhost:")):
        raise ValueError("Local deployment requires a local Docker context, not a remote host")
    env = dict(os.environ, API_IMAGE=args.image, API_ENV_FILE=str(root / ".env"),
               API_PORT=str(args.port))
    run("docker", "compose", "--project-name", "api-release", "--env-file", str(root / ".env"),
        "-f", str(root / "deploy/release/compose.yaml"), *commands, env=env)


def local_credentials():
    values = dict(line.split("=", 1) for line in (workspace() / ".env").read_text().splitlines()
                  if "=" in line and not line.startswith("#"))
    return json.loads(values["CREDENTIALS_JSON"].strip("'"))["acme"]["api_key"]


def request(url, key=None, payload=None, idempotency=None):
    headers = {"X-API-Key": key} if key else {}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if idempotency:
        headers["Idempotency-Key"] = idempotency
    req = urllib.request.Request(url, headers=headers,
                                 data=json.dumps(payload).encode() if payload else None)
    # Never forward an API credential to a redirect destination.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    with urllib.request.build_opener(NoRedirect).open(req, timeout=15) as response:
        return json.load(response)


def smoke(args):
    production = args.environment == "production"
    base = (args.url if production else f"http://127.0.0.1:{args.port}").rstrip("/")
    key = os.getenv("API_SMOKE_KEY") if production else local_credentials()
    if not key or (production and not base.startswith("https://")):
        raise ValueError("Production smoke requires API_SMOKE_KEY and an HTTPS API_URL")
    for service in SERVICES:
        path = f"{base}/{service}/api/v1/{service}?limit=5"
        result = request(path, key)
        if not isinstance(result.get("items"), list):
            raise ValueError("Invalid list response from " + service)
        try:
            request(path)
        except urllib.error.HTTPError as error:
            if error.code != 401:
                raise ValueError("Unexpected unauthenticated status from " + service) from None
        else:
            raise ValueError("Unauthenticated access unexpectedly allowed for " + service)
    if not production:
        key_id = "release-smoke-" + uuid.uuid4().hex
        body = {"orders": [{"name": "release smoke", "customer_id": "customers-001",
                            "product_id": "products-001", "quantity": 1, "unit_price": 10}]}
        job = request(base + "/orders/api/v1/import-jobs", key, body, key_id)
        for _ in range(30):
            state = request(base + "/orders/api/v1/jobs/" + job["id"], key)
            if state["state"] == "succeeded":
                break
            if state["state"] == "failed":
                raise ValueError("Local worker import failed")
            time.sleep(1)
        else:
            raise ValueError("Local worker import timed out")
    print("Authenticated API and authentication-denial checks passed."
          + (" Local worker passed." if not production else " Production checks were read-only."))


def validate_production(args):
    if os.getenv("GITHUB_EVENT_NAME") in {"pull_request", "pull_request_target"}:
        raise ValueError("Pull request jobs cannot deploy production")
    if not args.context or not args.namespace:
        raise ValueError("Set API_KUBE_CONTEXT and API_NAMESPACE explicitly")
    if not re.fullmatch(r"[a-z0-9]([-a-z0-9]*[a-z0-9])?", args.namespace):
        raise ValueError("Invalid namespace")
    for name, value in (("API_IMAGE", args.image), ("API_GATEWAY_IMAGE", args.gateway_image)):
        if not DIGEST.fullmatch(value):
            raise ValueError(name + " must be an immutable registry/image@sha256:digest")
    if not args.otel_endpoint or not args.url.startswith("https://"):
        raise ValueError("Set API_OTEL_ENDPOINT and an HTTPS API_URL")


def production_manifest(args):
    """Production resources are separate from the sample DB/seed/monitoring manifests."""
    validate_production(args)
    items = []

    def resource(kind, name, spec, api="v1"):
        value = {"apiVersion": api, "kind": kind,
                 "metadata": {"name": name, "namespace": args.namespace}, "spec": spec}
        items.append(value)
        return value

    env = [
        {"name": "APP_ENV", "value": "production"},
        {"name": "CUSTOMERS_URL", "value": "http://customers:8000"},
        {"name": "OTEL_ENABLED", "value": "true"},
        {"name": "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
         "value": args.otel_endpoint.rstrip("/") + "/v1/traces"},
        {"name": "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
         "value": args.otel_endpoint.rstrip("/") + "/v1/metrics"},
    ]
    security = {"runAsNonRoot": True, "runAsUser": 10001, "runAsGroup": 10001,
                "allowPrivilegeEscalation": False, "readOnlyRootFilesystem": True,
                "capabilities": {"drop": ["ALL"]}}
    for name in (*SERVICES, "import-worker"):
        worker = name == "import-worker"
        container = {
            "name": "worker" if worker else name, "image": args.image,
            "envFrom": [{"secretRef": {"name": args.secret}}],
            "env": env + [{"name": "SERVICE_NAME", "value": "orders" if worker else name},
                          {"name": "ROOT_PATH", "value": "" if worker else "/" + name}],
            "securityContext": security,
            "resources": {"requests": {"cpu": "100m", "memory": "128Mi"},
                          "limits": {"cpu": "1000m", "memory": "512Mi"}},
            "volumeMounts": [{"name": "tmp", "mountPath": "/tmp"}],
        }
        if worker:
            container["command"] = ["python", "-m", "api_interview_lab.platform.worker"]
        else:
            container["ports"] = [{"containerPort": 8000}]
            for probe, path in (("readinessProbe", "ready"), ("livenessProbe", "live"),
                                ("startupProbe", "live")):
                container[probe] = {"httpGet": {"path": "/health/" + path, "port": 8000},
                                    "periodSeconds": 5,
                                    "failureThreshold": 30 if probe == "startupProbe" else 3}
        pod = {"automountServiceAccountToken": False,
               "securityContext": {"seccompProfile": {"type": "RuntimeDefault"}},
               "terminationGracePeriodSeconds": 70, "containers": [container],
               "volumes": [{"name": "tmp", "emptyDir": {"sizeLimit": "64Mi"}}],
               "topologySpreadConstraints": [{"maxSkew": 1,
                    "topologyKey": "kubernetes.io/hostname", "whenUnsatisfiable": "ScheduleAnyway",
                    "labelSelector": {"matchLabels": {"app": name}}}]}
        if args.pull_secret:
            pod["imagePullSecrets"] = [{"name": args.pull_secret}]
        resource("Deployment", name, {
            # HPA owns service replica counts; omit replicas on repeated apply.
            **({"replicas": 1} if worker else {}),
            "revisionHistoryLimit": 5, "progressDeadlineSeconds": 300,
            "selector": {"matchLabels": {"app": name}},
            "strategy": {"type": "RollingUpdate", "rollingUpdate": {
                "maxSurge": 1, "maxUnavailable": 0}},
            "template": {"metadata": {"labels": {"app": name}}, "spec": pod},
        }, "apps/v1")
        if not worker:
            resource("Service", name, {"selector": {"app": name},
                "ports": [{"port": 8000, "targetPort": 8000}], "type": "ClusterIP"})
            resource("HorizontalPodAutoscaler", name, {
                "scaleTargetRef": {"apiVersion": "apps/v1", "kind": "Deployment", "name": name},
                "minReplicas": 2, "maxReplicas": 6,
                "metrics": [{"type": "Resource", "resource": {"name": "cpu", "target": {
                    "type": "Utilization", "averageUtilization": 65}}}],
                "behavior": {"scaleDown": {"stabilizationWindowSeconds": 120}},
            }, "autoscaling/v2")
            resource("PodDisruptionBudget", name, {"minAvailable": 1,
                "selector": {"matchLabels": {"app": name}}}, "policy/v1")
    # Resolve stable service names on each request through variables, using the configured DNS IP.
    if not re.fullmatch(r"[0-9a-fA-F:.]+", args.dns):
        raise ValueError("API_CLUSTER_DNS must be the cluster DNS service IP")
    config = """pid /tmp/nginx.pid;
events {}
http {
  client_body_temp_path /tmp/client_temp;
  proxy_temp_path /tmp/proxy_temp;
  resolver DNS_IP valid=10s;
  server {
    listen 8080;
    server_tokens off;
    client_max_body_size 64k;
    location = /health/live { return 200 'ok'; }
    location ~ ^/(orders|customers|products)(/.*)$ {
      set $backend $1.NAMESPACE.svc.cluster.local;
      set $rest $2;
      proxy_pass http://$backend:8000$rest$is_args$args;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-Proto https;
      proxy_connect_timeout 2s;
      proxy_read_timeout 5s;
      proxy_next_upstream off;
    }
    location / { return 404; }
  }
}
""".replace("DNS_IP", args.dns).replace("NAMESPACE", args.namespace)
    items.append({"apiVersion": "v1", "kind": "ConfigMap", "metadata": {
        "name": "gateway-config", "namespace": args.namespace}, "data": {"nginx.conf": config}})
    resource("Deployment", "gateway", {
        "replicas": 2, "progressDeadlineSeconds": 300,
        "strategy": {"type": "RollingUpdate", "rollingUpdate": {
            "maxSurge": 1, "maxUnavailable": 0}},
        "selector": {"matchLabels": {"app": "gateway"}},
        "template": {"metadata": {"labels": {"app": "gateway"}, "annotations": {
            "config-sha256": hashlib.sha256(config.encode()).hexdigest()}}, "spec": {
            "automountServiceAccountToken": False,
            "containers": [{"name": "gateway", "image": args.gateway_image,
                "command": ["nginx", "-g", "daemon off;"],
                "securityContext": {**security, "runAsUser": 101, "runAsGroup": 101},
                "ports": [{"containerPort": 8080}],
                "resources": {"requests": {"cpu": "100m", "memory": "64Mi"},
                              "limits": {"cpu": "500m", "memory": "256Mi"}},
                "readinessProbe": {"httpGet": {"path": "/health/live", "port": 8080}},
                "livenessProbe": {"httpGet": {"path": "/health/live", "port": 8080}},
                "volumeMounts": [{"name": "config", "mountPath": "/etc/nginx/nginx.conf",
                                  "subPath": "nginx.conf", "readOnly": True},
                                 {"name": "tmp", "mountPath": "/tmp"}]}],
            "securityContext": {"seccompProfile": {"type": "RuntimeDefault"}},
            "volumes": [{"name": "config", "configMap": {"name": "gateway-config"}},
                        {"name": "tmp", "emptyDir": {"sizeLimit": "64Mi"}}],
            **({"imagePullSecrets": [{"name": args.pull_secret}]} if args.pull_secret else {}),
        }},
    }, "apps/v1")
    resource("Service", "gateway", {"selector": {"app": "gateway"},
        "ports": [{"port": 8080, "targetPort": 8080}], "type": "ClusterIP"})
    return {"apiVersion": "v1", "kind": "List", "items": items}


def kubectl(args, *commands, **kwargs):
    return run("kubectl", "--context", args.context, "--namespace", args.namespace,
               *commands, **kwargs)


def schema_manifest(args):
    validate_production(args)
    return {"apiVersion": "batch/v1", "kind": "Job", "metadata": {
        "name": "api-initial-schema", "namespace": args.namespace}, "spec": {
        "backoffLimit": 0, "activeDeadlineSeconds": 180,
        "template": {"spec": {
            "restartPolicy": "Never", "automountServiceAccountToken": False,
            **({"imagePullSecrets": [{"name": args.pull_secret}]} if args.pull_secret else {}),
            "containers": [{"name": "schema", "image": args.image,
                "command": ["python", "-m", "api_interview_lab.platform.schema"],
                "env": [{"name": "APP_ENV", "value": "production"}],
                "envFrom": [{"secretRef": {"name": "platform-schema-secrets"}}],
                "securityContext": {"runAsNonRoot": True, "runAsUser": 10001,
                    "allowPrivilegeEscalation": False, "readOnlyRootFilesystem": True,
                    "capabilities": {"drop": ["ALL"]}},
                "resources": {"requests": {"cpu": "100m", "memory": "128Mi"},
                              "limits": {"cpu": "500m", "memory": "256Mi"}},
            }],
        }}}}


def deploy_production(args):
    manifest = production_manifest(args)
    if not os.getenv("API_SMOKE_KEY"):
        raise ValueError("API_SMOKE_KEY is required before changing production")
    # Check access/prerequisites without retrieving secret values.
    kubectl(args, "get", "secret", args.secret, "-o", "name")
    if args.pull_secret:
        kubectl(args, "get", "secret", args.pull_secret, "-o", "name")
    existing = json.loads(kubectl(args, "get", "deployments", "-o", "json", capture=True))
    previous = {item["metadata"]["name"]: {
        c["name"]: c["image"] for c in item["spec"]["template"]["spec"]["containers"]}
        for item in existing["items"] if item["metadata"]["name"] in DEPLOYMENTS}
    out = workspace() / "dist"
    out.mkdir(exist_ok=True)
    (out / "previous-images.json").write_text(json.dumps(previous, indent=2) + "\n")
    (out / "production-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    payload = json.dumps(manifest)
    kubectl(args, "apply", "--dry-run=server", "-f", "-", input=payload)
    kubectl(args, "apply", "-f", "-", input=payload)
    for name in DEPLOYMENTS:
        kubectl(args, "rollout", "status", "deployment/" + name, "--timeout=300s")
    smoke(args)
    print("Production rollout and read-only smoke checks passed: " + args.image)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle", default="")
    p.add_argument("command", choices=["build", "deploy", "smoke", "status", "logs",
                                      "stop", "render", "render-schema", "rollback"])
    p.add_argument("--environment", choices=["local", "production"], default="local")
    p.add_argument("--image", default=os.getenv("API_IMAGE", "api-platform:local"))
    p.add_argument("--python-base", default=os.getenv("PYTHON_BASE", "python:3.12-slim"))
    p.add_argument("--platform", default=os.getenv("API_PLATFORM", "linux/amd64"))
    p.add_argument("--skip-build", action="store_true")
    p.add_argument("--port", type=int, default=int(os.getenv("API_PORT", "8080")))
    p.add_argument("--context", default=os.getenv("API_KUBE_CONTEXT", ""))
    p.add_argument("--namespace", default=os.getenv("API_NAMESPACE", ""))
    p.add_argument("--secret", default=os.getenv("API_SECRET", "platform-secrets"))
    p.add_argument("--pull-secret", default=os.getenv("API_PULL_SECRET", ""))
    p.add_argument("--url", default=os.getenv("API_URL", ""))
    p.add_argument("--otel-endpoint", default=os.getenv("API_OTEL_ENDPOINT", ""))
    p.add_argument("--dns", default=os.getenv("API_CLUSTER_DNS", ""))
    p.add_argument("--gateway-image", default=os.getenv("API_GATEWAY_IMAGE", ""))
    p.add_argument("--service", choices=DEPLOYMENTS, default="orders")
    return p


def main():
    args = parser().parse_args()
    if args.environment == "production":
        if args.command == "render":
            print(json.dumps(production_manifest(args), indent=2))
        elif args.command == "render-schema":
            print(json.dumps(schema_manifest(args), indent=2))
        elif args.command == "deploy":
            # Deliberately never rebuild, publish, seed, or create credentials in production.
            deploy_production(args)
        elif args.command == "rollback":
            if not args.context or not args.namespace:
                raise ValueError("Rollback requires explicit context and namespace")
            kubectl(args, "rollout", "undo", "deployment/" + args.service)
            kubectl(args, "rollout", "status", "deployment/" + args.service, "--timeout=300s")
        elif args.command == "smoke":
            smoke(args)
        elif args.command in {"status", "logs"}:
            if not args.context or not args.namespace:
                raise ValueError("Set context and namespace")
            if args.command == "status":
                kubectl(args, "get", "pods,services,hpa")
            else:
                kubectl(args, "logs", "deployment/" + args.service, "--tail=100")
        else:
            raise ValueError("Production accepts only deploy/render/smoke/status/logs/rollback")
    elif args.command == "build":
        build(args)
    elif args.command == "deploy":
        if not args.skip_build:
            build(args)
        if not (workspace() / ".env").exists():
            run(sys.executable, str(workspace() / "scripts/bootstrap.py"), cwd=workspace())
        compose(args, "up", "-d", "--no-build", "--wait", "--wait-timeout", "180")
        smoke(args)
    elif args.command == "smoke":
        smoke(args)
    elif args.command == "status":
        compose(args, "ps")
    elif args.command == "logs":
        compose(args, "logs", "--tail=100",
                "worker" if args.service == "import-worker" else args.service)
    elif args.command == "stop":
        compose(args, "down")
    else:
        raise ValueError(args.command + " is only available for production")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, subprocess.CalledProcessError, urllib.error.URLError) as error:
        raise SystemExit("Release failed: " + str(error)) from None
