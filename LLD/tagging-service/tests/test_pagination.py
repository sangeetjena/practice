import base64
import json
import unittest

from tagging_service.models import ValidationError
from tagging_service.pagination import decode_cursor


class CursorValidationTest(unittest.TestCase):
    def test_deep_json_is_validation_error(self):
        nested = "[" * 1500 + "0" + "]" * 1500
        cursor = base64.urlsafe_b64encode(nested.encode()).decode()
        with self.assertRaises(ValidationError):
            decode_cursor(cursor, ["tenant", "tags"], 1)

    def test_unpaired_surrogate_rejected_before_database(self):
        payload = {"v": 1, "scope": ["tenant", "tags"], "after": ["\ud800"]}
        cursor = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
        with self.assertRaises(ValidationError):
            decode_cursor(cursor, ["tenant", "tags"], 1)

    def test_boolean_is_not_a_cursor_version(self):
        payload = {"v": True, "scope": ["tenant", "tags"], "after": ["id"]}
        cursor = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
        with self.assertRaises(ValidationError):
            decode_cursor(cursor, ["tenant", "tags"], 1)
