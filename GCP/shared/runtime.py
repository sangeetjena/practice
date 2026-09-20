import json
import re
from datetime import date, timedelta
from urllib.parse import urlencode
from urllib.request import Request


def validate_window(start_date: str, end_date: str) -> tuple[date, date]:
    if not all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) for value in (start_date, end_date)):
        raise ValueError("Dates must use YYYY-MM-DD")
    start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    if not start < end:
        raise ValueError("start_date must be before exclusive end_date")
    if (end - start).days > 366:
        raise ValueError("Split backfills into windows no longer than 366 days")
    return start, end


def dates(start_date: str, end_date: str):
    start, end = validate_window(start_date, end_date)
    while start < end:
        yield start.isoformat()
        start += timedelta(days=1)


def normalize_order(line: str) -> dict:
    """A strict example contract; malformed input deliberately fails the batch."""
    row = json.loads(line)
    if not isinstance(row, dict):
        raise ValueError("Order must be a JSON object")
    for key in ("order_id", "customer_id", "event_date"):
        if not isinstance(row.get(key), str) or not row[key]:
            raise ValueError(f"Missing or invalid {key}")
    date.fromisoformat(row["event_date"])
    amount = row.get("amount_cents")
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise ValueError("amount_cents must be a nonnegative integer")
    return {key: row[key] for key in ("order_id", "customer_id", "event_date", "amount_cents")}


def fetch_partner_day(api_url: str, api_key: str, day: str) -> list[dict]:
    """Example API contract: GET ?date=YYYY-MM-DD returns a JSON array of orders.

    Redirects are disabled to avoid forwarding the credential to another host.
    Pagination/rate limits are provider-specific and must be added before adapting
    this deliberately bounded demonstration to a real integration.
    """
    from urllib.error import HTTPError, URLError
    from urllib.request import HTTPRedirectHandler, build_opener

    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    if not api_url.startswith("https://"):
        raise ValueError("An HTTPS endpoint is required")
    separator = "&" if "?" in api_url else "?"
    request = Request(api_url + separator + urlencode({"date": day}), headers={"X-API-Key": api_key})
    try:
        with build_opener(NoRedirect).open(request, timeout=60) as response:
            # Avoid an unbounded driver/worker download in the example.
            payload = response.read(10_000_001)
        if len(payload) > 10_000_000:
            raise ValueError("Example endpoint exceeded its 10 MB response limit")
        rows = json.loads(payload)
    except (HTTPError, URLError):
        # Do not include response bodies, headers, or tokens in exception text.
        raise RuntimeError("Partner API request failed; inspect provider health and access") from None
    if not isinstance(rows, list):
        raise ValueError("Expected a JSON array from the partner API")
    return [normalize_order(json.dumps(row)) for row in rows]
