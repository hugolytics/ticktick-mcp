#!/usr/bin/env python3
import sys
import logging
from ticktick_mcp.client import TickTickClientSingleton


def run_once():
    client = TickTickClientSingleton.get_client()
    if client is None:
        logging.error("OAuth flow failed; check earlier logs.")
        sys.exit(1)
    print("✅ OAuth token obtained and cached via existing singleton.")


if __name__ == "__main__":
    run_once()
