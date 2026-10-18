import json
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from health_server import start_health_server, stop_health_server


class HealthServerTests(unittest.TestCase):
    def setUp(self):
        self.server, self.thread = start_health_server(0)
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        stop_health_server(self.server, self.thread)

    def test_health_path_returns_json_ok(self):
        with urlopen(f"{self.base_url}/health", timeout=2) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(
                response.headers.get_content_type(),
                "application/json",
            )
            payload = json.loads(response.read())

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "noise-remover-bot")

    def test_root_path_is_available_for_basic_probes(self):
        with urlopen(f"{self.base_url}/", timeout=2) as response:
            self.assertEqual(response.status, 200)

    def test_unknown_path_returns_not_found(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(f"{self.base_url}/missing", timeout=2)

        self.assertEqual(error.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
