"""Authenticated Pub/Sub delivery and the transactional-outbox relay.

Example: an outbox row becomes {event_id: 'uuid'} on the topic. Only after the
worker persists completion does its HTTP handler return 204. Publish-before-mark
can duplicate a delivery, so the stable event ID is deliberately preserved.
"""

import base64
import binascii
import json

from fastapi import HTTPException
from google.auth.transport.requests import Request
from google.oauth2 import id_token


def verify_service_identity(authorization, audience, service_account):
    if (
        not audience
        or not service_account
        or not authorization
        or not authorization.startswith("Bearer ")
    ):
        raise HTTPException(401, "authenticated service identity required")
    try:
        claims = id_token.verify_oauth2_token(authorization[7:], Request(), audience=audience)
    except (ValueError, TypeError) as error:
        raise HTTPException(401, "invalid service identity") from error
    if claims.get("email") != service_account or claims.get("email_verified") is not True:
        raise HTTPException(403, "unexpected service identity")


def decode_event(envelope):
    try:
        encoded = envelope["message"]["data"]
        if len(encoded) > 4096:
            raise ValueError("envelope too large")
        payload = json.loads(base64.b64decode(encoded, validate=True))
        event_id = payload["event_id"]
        import uuid

        return str(uuid.UUID(event_id))
    except (ValueError, KeyError, TypeError, binascii.Error) as error:
        raise HTTPException(400, "invalid event envelope") from error


class OutboxPublisher:
    def __init__(self, db, topic, client=None):
        self.db, self.topic = db, topic
        if client is None:
            from google.cloud import pubsub_v1

            client = pubsub_v1.PublisherClient()
        self.client = client

    def publish(self, limit=20):
        count = 0
        for event in self.db.pending(limit):
            self.client.publish(self.topic, json.dumps({"event_id": event["id"]}).encode()).result(
                timeout=15
            )
            self.db.published(event["id"])
            count += 1
        return count
