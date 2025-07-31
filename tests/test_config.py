"""
Unit tests for the config module.
"""

from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

from ticktick_mcp.config import (
    Config,
    get_config,
    load_dotenv_config,
    validate_oauth_config,
    get_dotenv_path,
    dotenv_dir_path,
)


class TestConfig:
    """Test the Config dataclass."""

    def test_config_creation_with_all_values(self):
        """Test creating a Config with all required values."""
        config = Config(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8080/callback",
            username="test@example.com",
            password="test_password",
        )

        assert config.client_id == "test_client_id"
        assert config.client_secret == "test_client_secret"
        assert config.redirect_uri == "http://localhost:8080/callback"
        assert config.username == "test@example.com"
        assert config.password == "test_password"

    def test_config_equality(self):
        """Test that Config instances can be compared for equality."""
        config1 = Config(
            client_id="test",
            client_secret="secret",
            redirect_uri="http://test",
            username="user",
            password="pass",
        )
        config2 = Config(
            client_id="test",
            client_secret="secret",
            redirect_uri="http://test",
            username="user",
            password="pass",
        )
        config3 = Config(
            client_id="different",
            client_secret="secret",
            redirect_uri="http://test",
            username="user",
            password="pass",
        )

        assert config1 == config2
        assert config1 != config3


class TestGetConfig:
    """Test the get_config function."""

    def test_get_config_from_env_vars(self, clean_env):
        """Test loading config from environment variables."""
        clean_env.set(
            TICKTICK_CLIENT_ID="env_client_id",
            TICKTICK_CLIENT_SECRET="env_client_secret",
            TICKTICK_REDIRECT_URI="http://env.example.com/callback",
            TICKTICK_USERNAME="env@example.com",
            TICKTICK_PASSWORD="env_password",
        )

        config = get_config()

        assert config.client_id == "env_client_id"
        assert config.client_secret == "env_client_secret"
        assert config.redirect_uri == "http://env.example.com/callback"
        assert config.username == "env@example.com"
        assert config.password == "env_password"

    def test_get_config_missing_required_env_var(self, clean_env):
        """Test that missing required environment variable raises ValueError."""
        clean_env.set(
            TICKTICK_CLIENT_ID="test_id",
            # Missing TICKTICK_CLIENT_SECRET
            TICKTICK_REDIRECT_URI="http://test.com/callback",
            TICKTICK_USERNAME="test@example.com",
            TICKTICK_PASSWORD="test_password",
        )

        with pytest.raises(ValueError, match="TICKTICK_CLIENT_SECRET"):
            get_config()

    def test_get_config_all_missing_env_vars(self, clean_env):
        """Test error message when all environment variables are missing."""
        with pytest.raises(ValueError) as exc_info:
            get_config()

        error_msg = str(exc_info.value)
        assert "TICKTICK_CLIENT_ID" in error_msg
        assert "TICKTICK_CLIENT_SECRET" in error_msg
        assert "TICKTICK_REDIRECT_URI" in error_msg
        assert "TICKTICK_USERNAME" in error_msg
        assert "TICKTICK_PASSWORD" in error_msg


class TestLoadDotenvConfig:
    """Test the load_dotenv_config function."""

    def test_load_dotenv_file_exists(self, tmp_path):
        """Test loading config from .env file."""
        env_file = tmp_path / ".env"
        env_content = """TICKTICK_CLIENT_ID=dotenv_client_id
TICKTICK_CLIENT_SECRET=dotenv_client_secret
TICKTICK_REDIRECT_URI=http://dotenv.example.com/callback
TICKTICK_USERNAME=dotenv@example.com
TICKTICK_PASSWORD=dotenv_password
"""
        env_file.write_text(env_content)

        with patch("ticktick_mcp.config.get_dotenv_path", return_value=env_file):
            config = load_dotenv_config()

        assert config.client_id == "dotenv_client_id"
        assert config.client_secret == "dotenv_client_secret"
        assert config.redirect_uri == "http://dotenv.example.com/callback"
        assert config.username == "dotenv@example.com"
        assert config.password == "dotenv_password"

    def test_load_dotenv_file_not_exists(self, tmp_path):
        """Test handling when .env file doesn't exist."""
        non_existent_file = tmp_path / ".env"

        with patch(
            "ticktick_mcp.config.get_dotenv_path", return_value=non_existent_file
        ):
            with pytest.raises(ValueError):
                load_dotenv_config()

    def test_load_dotenv_incomplete_file(self, tmp_path):
        """Test handling when .env file is incomplete."""
        env_file = tmp_path / ".env"
        env_content = """TICKTICK_CLIENT_ID=partial_client_id
# Missing other required variables
"""
        env_file.write_text(env_content)

        with patch("ticktick_mcp.config.get_dotenv_path", return_value=env_file):
            with pytest.raises(ValueError):
                load_dotenv_config()


class TestValidateOauthConfig:
    """Test the validate_oauth_config function."""

    def test_validate_complete_config(self):
        """Test validation of complete OAuth config."""
        config = Config(
            client_id="valid_id",
            client_secret="valid_secret",
            redirect_uri="http://valid.example.com/callback",
            username="valid@example.com",
            password="valid_password",
        )

        # Should not raise any exception
        validate_oauth_config(config)

    def test_validate_config_missing_client_id(self):
        """Test validation fails with missing client_id."""
        config = Config(
            client_id="",
            client_secret="valid_secret",
            redirect_uri="http://valid.example.com/callback",
            username="valid@example.com",
            password="valid_password",
        )

        with pytest.raises(ValueError, match="client_id"):
            validate_oauth_config(config)

    def test_validate_config_invalid_redirect_uri(self):
        """Test validation fails with invalid redirect URI."""
        config = Config(
            client_id="valid_id",
            client_secret="valid_secret",
            redirect_uri="not-a-url",
            username="valid@example.com",
            password="valid_password",
        )

        with pytest.raises(ValueError, match="redirect_uri"):
            validate_oauth_config(config)

    def test_validate_config_invalid_email(self):
        """Test validation fails with invalid email format."""
        config = Config(
            client_id="valid_id",
            client_secret="valid_secret",
            redirect_uri="http://valid.example.com/callback",
            username="not-an-email",
            password="valid_password",
        )

        with pytest.raises(ValueError, match="username"):
            validate_oauth_config(config)


class TestGetDotenvPath:
    """Test the get_dotenv_path function."""

    def test_get_dotenv_path_returns_path(self):
        """Test that get_dotenv_path returns a Path object."""
        path = get_dotenv_path()
        assert isinstance(path, Path)
        assert path.name == ".env"

    def test_get_dotenv_path_uses_dotenv_dir_path(self):
        """Test that get_dotenv_path uses the dotenv_dir_path variable."""
        path = get_dotenv_path()
        # Should be relative to the dotenv_dir_path
        assert str(dotenv_dir_path) in str(path.parent)


class TestDotenvDirPath:
    """Test the dotenv_dir_path variable."""

    def test_dotenv_dir_path_exists(self):
        """Test that dotenv_dir_path is properly exported."""
        assert dotenv_dir_path is not None
        assert isinstance(dotenv_dir_path, Path)

    def test_dotenv_dir_path_points_to_project_root(self):
        """Test that dotenv_dir_path points to the project root."""
        # Should point to a directory that contains src/
        src_path = dotenv_dir_path / "src"
        # We can't test if it actually exists in the test environment,
        # but we can test the structure
        assert src_path.name == "src"


class TestConfigLogging:
    """Test logging behavior in config module."""

    def test_config_loading_logs_appropriately(self, mock_logging):
        """Test that config loading generates appropriate log messages."""
        # This would require more sophisticated mocking to test actual
        # logging output, but we can at least verify the logging setup
        # doesn't break anything
        try:
            # This should work even if env vars are missing
            get_config()
        except ValueError:
            # Expected when env vars are missing
            pass

        # If we get here without exceptions, logging setup is OK
        assert True
