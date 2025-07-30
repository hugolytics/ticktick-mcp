#!/usr/bin/env python3
import os, logging
from ticktick_mcp import config
from ticktick_mcp.mcp_instance import mcp

# register all built‑in tools
logging.info("Registering MCP tools…")
from ticktick_mcp.tools import task_tools, filter_tools, conversion_tools
logging.info("Tools ready.")

if __name__ == "__main__":
    mcp.run(
        transport   = os.getenv("SERVER_TRANSPORT", "http"),
        host        = os.getenv("SERVER_HOST",      "0.0.0.0"),
        port        = int(os.getenv("SERVER_PORT",   "8150")),
    )
