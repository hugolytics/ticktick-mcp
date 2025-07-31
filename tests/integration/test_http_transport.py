"""
HTTP transport integration tests.
"""
import pytest
import httpx
import json
import uuid


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_via_tool_call(http_server):
    """Test that the server is healthy by calling the healthcheck tool."""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {
            "name": "healthcheck",
            "arguments": {}
        }
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{http_server}/", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == payload["id"]
    assert "result" in body
    # The result should contain status: ok from our healthcheck tool


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_call_over_http(http_server):
    """Test that a tool call works over HTTP JSON-RPC."""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {
            "name": "healthcheck",
            "arguments": {}
        }
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{http_server}/", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == payload["id"]
    assert "result" in body
