"""
HTTP server fixture for integration tests.
"""
import os
import sys
import socket
import subprocess
import time
import tempfile
import pytest
import httpx


@pytest.fixture(scope="session")
def http_server():
    """Spawn MCP in HTTP mode on a free port, yield (base_url, proc)."""
    # Pick free port
    sock = socket.socket()
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()

    env = os.environ.copy()
    env.update({
        "SERVER_TRANSPORT": "http",
        "SERVER_HOST": "0.0.0.0",
        "SERVER_PORT": str(port),
        # Fake creds to satisfy config loader
        "TICKTICK_CLIENT_ID": "dummy",
        "TICKTICK_CLIENT_SECRET": "dummy",
        "TICKTICK_REDIRECT_URI": "http://localhost/cb",
        "TICKTICK_USERNAME": "dummy@example.com",
        "TICKTICK_PASSWORD": "dummy",
        "HOME": tempfile.mkdtemp(),  # isolate token cache
    })

    # Start the server
    proc = subprocess.Popen(
        [sys.executable, "main.py"],  # use root main.py entry point
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait up to 15 s for server to be ready
    base = f"http://localhost:{port}"
    test_payload = {
        "jsonrpc": "2.0",
        "id": "test",
        "method": "tools/call",
        "params": {"name": "healthcheck", "arguments": {}}
    }
    
    for _ in range(60):
        try:
            response = httpx.post(f"{base}/", json=test_payload, timeout=1)
            if response.status_code == 200:
                break
        except Exception:
            time.sleep(0.25)
    else:
        proc.terminate()
        pytest.fail("Server failed to start within 15 s")

    yield base
    proc.terminate()
    proc.wait(timeout=5)
