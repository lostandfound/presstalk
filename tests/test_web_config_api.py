import sys
from pathlib import Path

# Ensure package import works when running directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import json
import os
import tempfile
import threading
import time
import unittest
from http.client import HTTPConnection

from presstalk.web_config import server as web_server  # type: ignore
from pathlib import Path
import sys



def _start_server(cfg_path: str):
    static_dir = Path(web_server.__file__).resolve().parent / "static"

    def _handler(*args, **kwargs):  # type: ignore
        return web_server._Handler(  # type: ignore[attr-defined]
            *args, static_dir=static_dir, cfg_path=cfg_path, **kwargs
        )

    httpd = web_server.HTTPServer(("127.0.0.1", 0), _handler)  # type: ignore[attr-defined]
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    # Give the server a moment to start
    time.sleep(0.02)
    return httpd, port, t


class TestWebConfigAPI(unittest.TestCase):
    def _tmp_yaml(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".yaml")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def _conn(self, port: int) -> HTTPConnection:
        return HTTPConnection("127.0.0.1", port, timeout=2)

    def test_get_config_returns_values(self):
        path = self._tmp_yaml(
            "# header\nlanguage: ja\nmodel: small\nhotkey: ctrl+space  # cmt\naudio_feedback: true\n"
        )
        httpd, port, _t = _start_server(path)
        try:
            c = self._conn(port)
            c.request("GET", "/api/config")
            r = c.getresponse()
            self.assertEqual(r.status, 200)
            data = json.loads(r.read().decode("utf-8"))
            self.assertEqual(data["language"], "ja")
            self.assertEqual(data["model"], "small")
            self.assertEqual(data["hotkey"], "ctrl+space")
            self.assertTrue(bool(data["audio_feedback"]))
        finally:
            httpd.shutdown()
            httpd.server_close()
            os.remove(path)

    def test_post_updates_yaml_and_normalizes_hotkey(self):
        path = self._tmp_yaml(
            "# header\nlanguage: ja\nmodel: small\nhotkey: ctrl+space  # cmt\naudio_feedback: true\n"
        )
        httpd, port, _t = _start_server(path)
        try:
            payload = {
                "language": "en",
                "model": "base",
                "hotkey": "SHIFT+SPACE",
                "audio_feedback": False,
            }
            c = self._conn(port)
            body = json.dumps(payload).encode("utf-8")
            c.request("POST", "/api/config", body=body, headers={"Content-Type": "application/json"})
            r = c.getresponse()
            self.assertEqual(r.status, 200)
            res = json.loads(r.read().decode("utf-8"))
            self.assertTrue(res.get("ok"))
            # Verify YAML updated and comment preserved
            text = Path(path).read_text(encoding="utf-8")
            self.assertIn("language: en", text)
            self.assertIn("model: base", text)
            self.assertIn("hotkey: shift+space  # cmt", text)
            self.assertIn("audio_feedback: false", text)
        finally:
            httpd.shutdown()
            httpd.server_close()
            os.remove(path)

    def test_post_rejects_large_request(self):
        path = self._tmp_yaml(
            "language: ja\nmodel: small\nhotkey: ctrl+space\naudio_feedback: true\n"
        )
        httpd, port, _t = _start_server(path)
        try:
            c = self._conn(port)
            payload = {"x": "y" * 9000}
            body = json.dumps(payload).encode("utf-8")
            c.request("POST", "/api/config", body=body, headers={"Content-Type": "application/json"})
            r = c.getresponse()
            self.assertEqual(r.status, 400)
        finally:
            httpd.shutdown()
            httpd.server_close()
            os.remove(path)

    def test_post_invalid_model_is_ignored(self):
        path = self._tmp_yaml(
            "language: ja\nmodel: small\nhotkey: ctrl+space\naudio_feedback: true\n"
        )
        httpd, port, _t = _start_server(path)
        try:
            c = self._conn(port)
            body = json.dumps({"model": "giant"}).encode("utf-8")
            c.request("POST", "/api/config", body=body, headers={"Content-Type": "application/json"})
            r = c.getresponse()
            _ = r.read()
            text = Path(path).read_text(encoding="utf-8")
            self.assertIn("model: small", text)
        finally:
            httpd.shutdown()
            httpd.server_close()
            os.remove(path)

    def test_post_invalid_hotkey_is_ignored(self):
        path = self._tmp_yaml(
            "language: ja\nmodel: small\nhotkey: ctrl+space\naudio_feedback: true\n"
        )
        httpd, port, _t = _start_server(path)
        try:
            c = self._conn(port)
            body = json.dumps({"hotkey": "ctrl+alt"}).encode("utf-8")
            c.request("POST", "/api/config", body=body, headers={"Content-Type": "application/json"})
            r = c.getresponse()
            _ = r.read()
            text = Path(path).read_text(encoding="utf-8")
            self.assertIn("hotkey: ctrl+space", text)
        finally:
            httpd.shutdown()
            httpd.server_close()
            os.remove(path)

    def test_validate_hotkey_endpoint(self):
        path = self._tmp_yaml(
            "language: ja\nmodel: small\nhotkey: ctrl+space\naudio_feedback: true\n"
        )
        httpd, port, _t = _start_server(path)
        try:
            c = self._conn(port)
            body = json.dumps({"hotkey": "ctrl+shift+x"}).encode("utf-8")
            c.request("POST", "/api/validate/hotkey", body=body, headers={"Content-Type": "application/json"})
            r = c.getresponse()
            self.assertEqual(r.status, 200)
            j = json.loads(r.read().decode("utf-8"))
            self.assertTrue(j.get("ok"))
            self.assertTrue(j.get("valid"))
            self.assertEqual(j.get("normalized"), "ctrl+shift+x")
        finally:
            httpd.shutdown()
            httpd.server_close()
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
