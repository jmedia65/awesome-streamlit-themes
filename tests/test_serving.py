"""Check the real Studio server's public file-serving boundary."""

from http.client import HTTPConnection
import socket
import subprocess
import sys
import time
from urllib.parse import urlsplit

import pytest

from studio.catalog import ROOT


def request(port, path):
    """Preserve encoded paths and follow only local redirects."""
    for _ in range(5):
        connection = HTTPConnection("127.0.0.1", port, timeout=5)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            body = response.read()
            status = response.status
            location = response.getheader("Location")
        finally:
            connection.close()
        if status not in {301, 302, 307, 308}:
            return status, body
        target = urlsplit(location)
        assert not target.netloc or (target.hostname == "127.0.0.1" and target.port == port)
        path = target.path or "/"
        if target.query:
            path += "?" + target.query
    raise AssertionError("Too many redirects")


@pytest.fixture(scope="module")
def studio_server(tmp_path_factory):
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    log_path = tmp_path_factory.mktemp("studio-server") / "server.log"
    with log_path.open("wb") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "studio", "--server.address=127.0.0.1", f"--server.port={port}"],
            cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    pytest.fail(f"Studio exited before readiness: {log_path.read_text()}")
                try:
                    if request(port, "/_stcore/health") == (200, b"ok"):
                        break
                except OSError:
                    pass
                time.sleep(0.1)
            else:
                pytest.fail(f"Studio did not become ready: {log_path.read_text()}")
            yield port
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def test_repository_files_and_traversal_are_not_public_downloads(studio_server):
    status, shell = request(studio_server, "/")
    assert status == 200 and b'<div id="root"' in shell
    paths = (
        "/README.md", "/studio/README.md", "/studio/streamlit_app.py",
        "/requirements.txt", "/runtime.txt", "/themes/",
        "/themes/healthcare/.streamlit/config.toml", "/licenses/FONT_NOTICES.md",
        "/docs/private.md", "/.git/config",
        "/.streamlit/config.toml", "/.streamlit/secrets.toml",
        "/app/static/", "/app/static/../README.md",
        "/app/static/%2e%2e/README.md", "/app/static/%2e%2e/%2e%2e/README.md",
        "/app/static/..%2f..%2fREADME.md", "/app/static/%2fetc/passwd",
        "/app/static/%252e%252e%252fREADME.md",
    )
    for path in paths:
        status, body = request(studio_server, path)
        assert status in {200, 400, 403, 404}, (path, status)
        # Unknown frontend routes may return the app shell, never repository bytes.
        if status == 200:
            assert body == shell, path


def test_intended_public_font_is_served(studio_server):
    status, body = request(studio_server, "/app/static/Inter_18pt-Regular.ttf")
    assert status == 200
    assert body == (ROOT / "themes/financial/static/Inter_18pt-Regular.ttf").read_bytes()
