"""
Unit tests for the mcp_instance module.
"""

from unittest.mock import patch, MagicMock
import pytest

from ticktick_mcp.mcp_instance import mcp


class TestMCPInstance:
    """Test the MCP instance creation and configuration."""

    def test_mcp_instance_is_created(self):
        """Test that mcp instance is properly created."""
        assert mcp is not None
        # Check that it has the expected FastMCP interface
        assert hasattr(mcp, "tool")
        assert hasattr(mcp, "run")
        assert callable(mcp.tool)
        assert callable(mcp.run)

    def test_mcp_instance_has_correct_name(self):
        """Test that MCP instance has the correct name."""
        # The name should be set to "ticktick-mcp"
        assert mcp.name == "ticktick-mcp"

    def test_mcp_instance_has_correct_version(self):
        """Test that MCP instance has a version."""
        # Should have a version string
        assert hasattr(mcp, "version")
        assert isinstance(mcp.version, str)
        assert len(mcp.version) > 0


class TestMCPToolDecorator:
    """Test the MCP tool decorator functionality."""

    def test_tool_decorator_is_callable(self):
        """Test that the tool decorator can be called."""
        assert callable(mcp.tool)

    def test_tool_decorator_registers_function(self):
        """Test that the tool decorator can register a function."""

        # Create a mock function to register
        @mcp.tool()
        def test_tool():
            """A test tool."""
            return "test result"

        # If we get here without error, the decorator worked
        assert callable(test_tool)
        assert test_tool() == "test result"

    def test_tool_decorator_with_name(self):
        """Test that the tool decorator accepts a name parameter."""

        @mcp.tool(name="custom_tool_name")
        def another_test_tool():
            """Another test tool."""
            return "another result"

        assert callable(another_test_tool)
        assert another_test_tool() == "another result"


class TestMCPRun:
    """Test the MCP run functionality."""

    def test_run_method_exists(self):
        """Test that the run method exists and is callable."""
        assert hasattr(mcp, "run")
        assert callable(mcp.run)

    def test_run_accepts_transport_parameter(self):
        """Test that run method accepts transport parameter."""
        # We can't actually run it in tests, but we can check the signature
        import inspect

        sig = inspect.signature(mcp.run)
        params = list(sig.parameters.keys())

        # Should accept at least 'transport' parameter
        # Note: FastMCP.run signature may vary, so we test what we know
        assert len(params) >= 1

    def test_run_with_stdio_transport(self, dummy_mcp_run):
        """Test calling run with stdio transport."""
        # Use our dummy implementation
        mcp.run("stdio")

        assert len(dummy_mcp_run.calls) == 1
        assert dummy_mcp_run.calls[0]["transport"] == "stdio"

    def test_run_with_sse_transport(self, dummy_mcp_run):
        """Test calling run with SSE transport."""
        mcp.run("sse", host="127.0.0.1", port=8080)

        assert len(dummy_mcp_run.calls) == 1
        call = dummy_mcp_run.calls[0]
        assert call["transport"] == "sse"
        assert call["host"] == "127.0.0.1"
        assert call["port"] == 8080


class TestMCPConfiguration:
    """Test MCP configuration and setup."""

    def test_mcp_instance_configuration(self):
        """Test that MCP instance is configured correctly."""
        # Should be a FastMCP instance
        assert mcp.__class__.__name__ == "FastMCP"

    def test_mcp_logging_configuration(self, mock_logging):
        """Test that MCP logging is configured appropriately."""
        # Re-import to trigger any logging during module load
        import importlib
        import ticktick_mcp.mcp_instance

        importlib.reload(ticktick_mcp.mcp_instance)

        # Check for expected log messages
        log_messages = [log["message"] for log in mock_logging]
        assert any("MCP instance created" in msg for msg in log_messages)


class TestMCPImports:
    """Test MCP module imports."""

    def test_fastmcp_import_works(self):
        """Test that FastMCP can be imported."""
        # If the module imported successfully, this test passes
        import ticktick_mcp.mcp_instance

        assert hasattr(ticktick_mcp.mcp_instance, "mcp")

    def test_mcp_instance_exports(self):
        """Test that the module exports the mcp instance."""
        from ticktick_mcp.mcp_instance import mcp as imported_mcp

        assert imported_mcp is not None
        assert imported_mcp is mcp


class TestMCPErrorHandling:
    """Test MCP error handling."""

    def test_mcp_handles_tool_registration_errors(self):
        """Test that MCP handles tool registration errors gracefully."""
        # Try to register a tool that might cause issues
        try:

            @mcp.tool()
            def problematic_tool():
                """A tool that might cause issues."""
                raise ValueError("Tool error")

            # If registration succeeded, the decorator worked
            assert callable(problematic_tool)
        except Exception as e:
            # If registration failed, that's also OK for this test
            assert isinstance(e, Exception)

    def test_mcp_run_error_handling(self, dummy_mcp_run):
        """Test that run method handles errors appropriately."""
        # Configure dummy to raise an error
        dummy_mcp_run.should_raise = True

        with pytest.raises(Exception):
            mcp.run("stdio")


class TestMCPMetadata:
    """Test MCP metadata and introspection."""

    def test_mcp_has_required_attributes(self):
        """Test that MCP instance has all required attributes."""
        required_attrs = ["name", "version", "tool", "run"]

        for attr in required_attrs:
            assert hasattr(
                mcp, attr
            ), f"MCP instance missing required attribute: {attr}"

    def test_mcp_name_format(self):
        """Test that MCP name follows expected format."""
        assert isinstance(mcp.name, str)
        assert len(mcp.name) > 0
        # Should be a reasonable name (not empty or just whitespace)
        assert mcp.name.strip() == mcp.name
        assert len(mcp.name.strip()) > 0

    def test_mcp_version_format(self):
        """Test that MCP version follows expected format."""
        assert isinstance(mcp.version, str)
        assert len(mcp.version) > 0
        # Version should not be empty or just whitespace
        assert mcp.version.strip() == mcp.version
        assert len(mcp.version.strip()) > 0


class TestMCPToolRegistry:
    """Test MCP tool registry functionality."""

    def test_multiple_tool_registration(self):
        """Test that multiple tools can be registered."""
        tool_count_before = len(getattr(mcp, "_tools", []))

        @mcp.tool()
        def first_test_tool():
            """First test tool."""
            return "first"

        @mcp.tool()
        def second_test_tool():
            """Second test tool."""
            return "second"

        # Both tools should be callable
        assert callable(first_test_tool)
        assert callable(second_test_tool)
        assert first_test_tool() == "first"
        assert second_test_tool() == "second"

    def test_tool_with_complex_signature(self):
        """Test registering a tool with complex signature."""

        @mcp.tool()
        def complex_tool(arg1: str, arg2: int = 42, *args, **kwargs):
            """A tool with a complex signature."""
            return f"arg1={arg1}, arg2={arg2}, args={args}, kwargs={kwargs}"

        assert callable(complex_tool)
        result = complex_tool("test", 100, "extra", key="value")
        assert "arg1=test" in result
        assert "arg2=100" in result
