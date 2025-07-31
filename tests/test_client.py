"""
Unit tests for the client module.
"""

from unittest.mock import patch, MagicMock
import pytest

from ticktick_mcp.client import get_client, _client_instance
from ticktick_mcp.config import Config


class TestGetClient:
    """Test the get_client singleton function."""

    def test_get_client_singleton_behavior(self, fake_config):
        """Test that get_client returns the same instance on multiple calls."""
        # Clear any existing singleton instance
        import ticktick_mcp.client

        ticktick_mcp.client._client_instance = None

        with patch("ticktick_mcp.client.get_config", return_value=fake_config):
            with patch("ticktick_mcp.client.TickTickClient") as mock_ticktick:
                mock_client = MagicMock()
                mock_ticktick.return_value = mock_client

                # First call should create instance
                client1 = get_client()

                # Second call should return same instance
                client2 = get_client()

                assert client1 is client2
                # TickTickClient constructor should only be called once
                mock_ticktick.assert_called_once()

    def test_get_client_creates_ticktick_client_with_config(self, fake_config):
        """Test that get_client creates TickTickClient with proper config."""
        # Clear any existing singleton instance
        import ticktick_mcp.client

        ticktick_mcp.client._client_instance = None

        with patch("ticktick_mcp.client.get_config", return_value=fake_config):
            with patch("ticktick_mcp.client.TickTickClient") as mock_ticktick:
                mock_client = MagicMock()
                mock_ticktick.return_value = mock_client

                client = get_client()

                # Verify TickTickClient was called with the config values
                mock_ticktick.assert_called_once_with(
                    username=fake_config.username,
                    password=fake_config.password,
                    oauth={
                        "client_id": fake_config.client_id,
                        "client_secret": fake_config.client_secret,
                        "redirect_uri": fake_config.redirect_uri,
                    },
                )
                assert client is mock_client

    def test_get_client_handles_config_error(self):
        """Test that get_client propagates config errors."""
        # Clear any existing singleton instance
        import ticktick_mcp.client

        ticktick_mcp.client._client_instance = None

        with patch(
            "ticktick_mcp.client.get_config", side_effect=ValueError("Config error")
        ):
            with pytest.raises(ValueError, match="Config error"):
                get_client()

    def test_get_client_handles_ticktick_client_error(self, fake_config):
        """Test that get_client propagates TickTickClient creation errors."""
        # Clear any existing singleton instance
        import ticktick_mcp.client

        ticktick_mcp.client._client_instance = None

        with patch("ticktick_mcp.client.get_config", return_value=fake_config):
            with patch(
                "ticktick_mcp.client.TickTickClient",
                side_effect=Exception("Client creation failed"),
            ):
                with pytest.raises(Exception, match="Client creation failed"):
                    get_client()

    def test_get_client_preserves_singleton_after_error(self, fake_config):
        """Test that singleton state is preserved even after errors."""
        # Clear any existing singleton instance
        import ticktick_mcp.client

        ticktick_mcp.client._client_instance = None

        # First call fails
        with patch(
            "ticktick_mcp.client.get_config", side_effect=ValueError("Config error")
        ):
            with pytest.raises(ValueError):
                get_client()

        # Second call succeeds and should create new instance
        with patch("ticktick_mcp.client.get_config", return_value=fake_config):
            with patch("ticktick_mcp.client.TickTickClient") as mock_ticktick:
                mock_client = MagicMock()
                mock_ticktick.return_value = mock_client

                client1 = get_client()
                client2 = get_client()

                assert client1 is client2
                mock_ticktick.assert_called_once()


class TestClientSingleton:
    """Test the singleton pattern implementation."""

    def test_singleton_instance_initially_none(self):
        """Test that singleton instance starts as None."""
        # This test assumes a fresh import
        import ticktick_mcp.client

        # Reset to initial state
        ticktick_mcp.client._client_instance = None

        assert ticktick_mcp.client._client_instance is None

    def test_singleton_instance_set_after_get_client(self, fake_config):
        """Test that singleton instance is set after calling get_client."""
        # Clear any existing singleton instance
        import ticktick_mcp.client

        ticktick_mcp.client._client_instance = None

        with patch("ticktick_mcp.client.get_config", return_value=fake_config):
            with patch("ticktick_mcp.client.TickTickClient") as mock_ticktick:
                mock_client = MagicMock()
                mock_ticktick.return_value = mock_client

                client = get_client()

                assert ticktick_mcp.client._client_instance is not None
                assert ticktick_mcp.client._client_instance is client


class TestClientImports:
    """Test that necessary imports work correctly."""

    def test_imports_work(self):
        """Test that all necessary imports are available."""
        # If we can import these without error, the test passes
        from ticktick_mcp.client import get_client, _client_instance

        assert callable(get_client)
        # _client_instance might be None, but should be accessible
        assert _client_instance is None or _client_instance is not None

    def test_ticktick_import_available(self):
        """Test that TickTick import is available in the module."""
        # This is a bit meta, but we want to ensure the import works
        import ticktick_mcp.client

        assert hasattr(ticktick_mcp.client, "TickTickClient")


class TestClientLogging:
    """Test logging behavior in client module."""

    def test_client_creation_logs_appropriately(self, mock_logging, fake_config):
        """Test that client creation generates appropriate log messages."""
        # Clear any existing singleton instance
        import ticktick_mcp.client

        ticktick_mcp.client._client_instance = None

        with patch("ticktick_mcp.client.get_config", return_value=fake_config):
            with patch("ticktick_mcp.client.TickTickClient") as mock_ticktick:
                mock_client = MagicMock()
                mock_ticktick.return_value = mock_client

                get_client()

        # Check for expected log messages
        log_messages = [log["message"] for log in mock_logging]
        assert any("Creating TickTick client" in msg for msg in log_messages)

    def test_singleton_reuse_logs_appropriately(self, mock_logging, fake_config):
        """Test that singleton reuse generates appropriate log messages."""
        # Clear any existing singleton instance
        import ticktick_mcp.client

        ticktick_mcp.client._client_instance = None

        with patch("ticktick_mcp.client.get_config", return_value=fake_config):
            with patch("ticktick_mcp.client.TickTickClient") as mock_ticktick:
                mock_client = MagicMock()
                mock_ticktick.return_value = mock_client

                # First call
                get_client()
                # Second call
                get_client()

        # Check for expected log messages
        log_messages = [log["message"] for log in mock_logging]
        assert any("Reusing existing TickTick client" in msg for msg in log_messages)


class TestClientConfiguration:
    """Test client configuration handling."""

    def test_oauth_config_structure(self, fake_config):
        """Test that OAuth config is structured correctly."""
        # Clear any existing singleton instance
        import ticktick_mcp.client

        ticktick_mcp.client._client_instance = None

        with patch("ticktick_mcp.client.get_config", return_value=fake_config):
            with patch("ticktick_mcp.client.TickTickClient") as mock_ticktick:
                mock_client = MagicMock()
                mock_ticktick.return_value = mock_client

                get_client()

                # Get the call arguments
                call_args, call_kwargs = mock_ticktick.call_args

                assert "oauth" in call_kwargs
                oauth_config = call_kwargs["oauth"]

                assert "client_id" in oauth_config
                assert "client_secret" in oauth_config
                assert "redirect_uri" in oauth_config

                assert oauth_config["client_id"] == fake_config.client_id
                assert oauth_config["client_secret"] == fake_config.client_secret
                assert oauth_config["redirect_uri"] == fake_config.redirect_uri
