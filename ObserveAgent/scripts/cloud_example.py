"""Client example: submit an incident and print its polling endpoint.

Set OBSERVE_API_URL and OBSERVE_API_KEY, run this script, and process queued events
with `cloud.admin drain` locally or the Pub/Sub worker in Google Cloud.
"""

import os
import uuid

import httpx

incident_id = "demo-" + uuid.uuid4().hex[:12]
with httpx.Client(
    base_url=os.getenv("OBSERVE_API_URL", "http://localhost:8091"),
    headers={"X-API-Key": os.environ["OBSERVE_API_KEY"]},
    timeout=30,
) as client:
    response = client.post(
        "/v1/incidents",
        headers={"Idempotency-Key": incident_id},
        json={"id": incident_id, "title": "Orders became slow", "service": "orders"},
    )
    response.raise_for_status()
    print(response.json())
    print("Process the event, then inspect:", f"/v1/incidents/{incident_id}")
    print("Use the same customer key when reading its messages or report.")
