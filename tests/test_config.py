"""
Unit tests for the Config class.
"""

import sys
import os
import pytest
from pathlib import Path

# Add the root directory to the path so we can import abigail
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abigail.config import Config


@pytest.fixture
def temp_config(tmp_path: Path) -> str:
    """
    Create a temporary config file path for testing.
    The file does not exist initially, so Config will use defaults.
    """
    config_file = tmp_path / "config.json"
    return str(config_file)


def test_config_defaults(temp_config: str) -> None:
    """Test that default configuration values are correct."""
    config = Config(config_file=temp_config)
    assert config.get("personality") == "tsundere"
    assert config.get("response_language") == "English"
    assert config.get("interface_language") == "English"
    assert config.get("chat_height") == 400
    assert config.get("font_family") == "sans-serif"
    assert config.get("font_size") == "medium"
    assert config.get("max_history") == 500
    assert config.get("context_messages") == 10


def test_config_get_missing_key(temp_config: str) -> None:
    """Test that getting a missing key returns None."""
    config = Config(config_file=temp_config)
    assert config.get("non_existent_key") is None


def test_config_get_with_default(temp_config: str) -> None:
    """Test that getting a missing key with a default returns the default."""
    config = Config(config_file=temp_config)
    assert config.get("non_existent_key", "default_value") == "default_value"


def test_config_set_and_save(temp_config: str) -> None:
    """Test that setting a value updates the config and saves it."""
    config = Config(config_file=temp_config)
    config.set("personality", "gentle")
    assert config.get("personality") == "gentle"

    # Create a new config instance to verify persistence
    new_config = Config(config_file=temp_config)
    assert new_config.get("personality") == "gentle"