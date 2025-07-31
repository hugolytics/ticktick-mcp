"""
Parametrised tests for CLI parsing and main() behaviour.
"""
from __future__ import annotations

from itertools import product
from typing import Mapping
from unittest.mock import patch

import pytest

from main import parse_args, main


# --------------------------------------------------------------------------- #
# CLI parsing: precedence matrix
# --------------------------------------------------------------------------- #

_env_sets: list[Mapping[str, str] | None] = [
    None,
    {"SERVER_TRANSPORT": "sse", "SERVER_HOST": "127.0.0.1", "SERVER_PORT": "9000"},
]

_cli_sets: list[list[str]] = [
    [],
    ["--transport", "streamable-http", "--host", "192.168.0.100", "--port", "3000"],
]


@pytest.mark.parametrize(
    ("env_vars", "cli_args"),
    list(product(_env_sets, _cli_sets)),
    ids=lambda v: "env" if isinstance(v, dict) else ("cli" if v else "none"),
)
def test_parse_args_precedence(clean_env, env_vars, cli_args):
    """Ensure CLI > ENV > defaults."""
    if env_vars:
        clean_env.set(**env_vars)

    with patch("sys.argv", ["main.py", *cli_args]):
        args = parse_args()

    if cli_args:
        assert (args.transport, args.host, args.port) == (
            "streamable-http",
            "192.168.0.100",
            3000,
        )
    elif env_vars:
        assert (args.transport, args.host, args.port) == (
            env_vars["SERVER_TRANSPORT"],
            env_vars["SERVER_HOST"],
            int(env_vars["SERVER_PORT"]),
        )
    else:
        assert (args.transport, args.host, args.port) == ("stdio", "0.0.0.0", 8150)


# --------------------------------------------------------------------------- #
# main() behaviour via DummyMCP
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "cli_args, expected",
    [
        ([], {"transport": "stdio", "host": "0.0.0.0", "port": 8150}),
        (
            ["--transport", "sse", "--host", "127.0.0.1", "--port", "9000"],
            {"transport": "sse", "host": "127.0.0.1", "port": 9000},
        ),
    ],
)
def test_main_invocation(clean_env, dummy_mcp, cli_args, expected):
    with patch("sys.argv", ["main.py", *cli_args]):
        main()

    assert dummy_mcp.run_calls[0] == expected
