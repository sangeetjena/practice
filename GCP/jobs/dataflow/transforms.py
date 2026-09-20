import hashlib
import json
from datetime import UTC, datetime

import apache_beam as beam

from shared.authentication.secrets import read_secret
from shared.runtime import fetch_partner_day, normalize_order


class ParseOrders(beam.PTransform):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def expand(self, lines):
        return (
            lines
            | "Parse contract" >> beam.Map(normalize_order)
            | "Filter window" >> beam.Filter(lambda row: self.start_date <= row["event_date"] < self.end_date)
            # Hash the complete row to remove exact duplicates without silently choosing
            # between two conflicting versions of the same order ID.
            | "Canonical JSON" >> beam.Map(lambda row: json.dumps(row, sort_keys=True))
            | "Remove exact duplicates" >> beam.Distinct()
            | "Decode JSON" >> beam.Map(json.loads)
        )


class FetchPartner(beam.DoFn):
    def __init__(self, api_url, secret_version):
        # Only the resource name enters Beam's serialized graph.
        self.api_url = api_url
        self.secret_version = secret_version

    def setup(self):
        # Executed on workers with their attached Dataflow service account.
        self.api_key = read_secret(self.secret_version)

    def process(self, day):
        for row in fetch_partner_day(self.api_url, self.api_key, day):
            if row["event_date"] != day:
                raise ValueError("Partner returned data outside the requested day")
            yield row


def metric_pair(row):
    return (row["customer_id"], row["event_date"]), row["amount_cents"]


def bigtable_row(item, family):
    from google.cloud.bigtable.row import DirectRow

    (customer_id, event_date), amount_cents = item
    # Salt high-cardinality row keys to reduce sequential-write hotspots.
    salt = hashlib.sha256(customer_id.encode()).hexdigest()[:2]
    row = DirectRow(f"{salt}#{customer_id}#{event_date}".encode())
    # Deterministic timestamp makes retries replace the same cell version.
    timestamp = datetime.fromisoformat(event_date).replace(tzinfo=UTC)
    row.set_cell(family, b"amount_cents", str(amount_cents).encode(), timestamp=timestamp)
    return row


class WriteMetrics(beam.DoFn):
    """Bounded bulk writes with an explicit application profile and surfaced row failures."""

    def __init__(self, project, instance, table, family, app_profile):
        self.project = project
        self.instance = instance
        self.table_id = table
        self.family = family
        self.app_profile = app_profile

    def setup(self):
        from google.cloud import bigtable

        self.client = bigtable.Client(project=self.project)
        self.table = self.client.instance(self.instance).table(self.table_id, app_profile_id=self.app_profile)

    def process(self, items):
        rows = [bigtable_row(item, self.family) for item in items]
        statuses = self.table.mutate_rows(rows)
        if len(statuses) != len(rows) or any(status.code != 0 for status in statuses):
            raise RuntimeError("Bigtable reported a failed row mutation")
        for (customer_id, event_date), amount in items:
            yield {"customer_id": customer_id, "event_date": event_date, "amount_cents": amount}
