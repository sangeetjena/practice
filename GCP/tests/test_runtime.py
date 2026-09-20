import json

import pytest

from shared.authentication.secrets import read_secret
from shared.runtime import dates, normalize_order, validate_window


def test_dates_are_end_exclusive_and_leap_year_aware():
    assert list(dates("2024-02-28", "2024-03-01")) == ["2024-02-28", "2024-02-29"]


@pytest.mark.parametrize(
    "start,end",
    [
        ("2026-02-30", "2026-03-01"),
        ("2026-03-01", "2026-03-01"),
        ("2026-03-02", "2026-03-01"),
        ("2024-01-01", "2026-01-01"),
        ("20260901", "2026-09-02"),
    ],
)
def test_bad_windows(start, end):
    with pytest.raises(ValueError):
        validate_window(start, end)


def test_money_stays_integer():
    row = {"order_id": "a", "customer_id": "b", "event_date": "2026-09-18", "amount_cents": 123}
    assert normalize_order(json.dumps(row))["amount_cents"] == 123
    for amount in (True, -1, 1.23, "123", None):
        row["amount_cents"] = amount
        with pytest.raises(ValueError):
            normalize_order(json.dumps(row))


def test_secret_reference_is_pinned_and_rejects_plaintext():
    with pytest.raises(ValueError):
        read_secret("super-secret-api-key")
    with pytest.raises(ValueError):
        read_secret("projects/p/secrets/s/versions/latest")


def test_secret_uses_runtime_adc(monkeypatch):
    from types import SimpleNamespace

    secretmanager = pytest.importorskip("google.cloud.secretmanager")
    seen = []

    class Client:
        def access_secret_version(self, request):
            seen.append(request)
            return SimpleNamespace(payload=SimpleNamespace(data=b"test-only-token"))

    monkeypatch.setattr(secretmanager, "SecretManagerServiceClient", Client)
    reference = "projects/p/secrets/partner/versions/3"
    assert read_secret(reference) == "test-only-token"
    assert seen == [{"name": reference}]
