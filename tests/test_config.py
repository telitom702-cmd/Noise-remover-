import unittest
from unittest.mock import patch

from config import _positive_int_env


class PositiveIntegerEnvironmentTests(unittest.TestCase):
    def test_uses_default_when_value_is_missing(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(_positive_int_env("APP_LIMIT", 7), 7)

    def test_reads_positive_integer_from_environment(self):
        with patch.dict("os.environ", {"APP_LIMIT": "12"}, clear=True):
            self.assertEqual(_positive_int_env("APP_LIMIT", 7), 12)

    def test_rejects_non_integer_value(self):
        with patch.dict("os.environ", {"APP_LIMIT": "many"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "APP_LIMIT"):
                _positive_int_env("APP_LIMIT", 7)

    def test_rejects_zero_and_negative_values(self):
        for value in ("0", "-3"):
            with self.subTest(value=value):
                with patch.dict("os.environ", {"APP_LIMIT": value}, clear=True):
                    with self.assertRaisesRegex(RuntimeError, "APP_LIMIT"):
                        _positive_int_env("APP_LIMIT", 7)


if __name__ == "__main__":
    unittest.main()
