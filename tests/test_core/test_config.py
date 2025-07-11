"""
Tests for configuration management.

Tests environment variable loading, client initialization, and validation.
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.core.config import Config


class TestConfiguration:
    """Test configuration management functionality."""

    def test_config_initialization_with_defaults(self, temp_dir):
        """Test configuration initialization with default values."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}, clear=True):
            config = Config()

            assert config.openai_api_key == "test_key"
            assert config.llm_model == "gpt-4"
            assert config.embedding_model == "text-embedding-3-small"
            assert config.max_conversation_history == 50
            assert config.chunk_size == 1000
            assert config.chunk_overlap == 200

    def test_config_initialization_with_custom_values(self, temp_dir):
        """Test configuration initialization with custom environment variables."""
        custom_env = {
            "OPENAI_API_KEY": "custom_key",
            "LLM_MODEL": "gpt-3.5-turbo",
            "EMBEDDING_MODEL": "custom-embedding",
            "MAX_CONVERSATION_HISTORY": "100",
            "CHUNK_SIZE": "500",
            "CHUNK_OVERLAP": "50",
            "VECTOR_STORE_PATH": str(temp_dir / "custom_vectors"),
            "SESSION_STORE_PATH": str(temp_dir / "custom_sessions")
        }

        with patch.dict(os.environ, custom_env, clear=True):
            config = Config()

            assert config.openai_api_key == "custom_key"
            assert config.llm_model == "gpt-3.5-turbo"
            assert config.embedding_model == "custom-embedding"
            assert config.max_conversation_history == 100
            assert config.chunk_size == 500
            assert config.chunk_overlap == 50

    def test_directory_creation(self, temp_dir):
        """Test that configuration creates necessary directories."""
        custom_env = {
            "OPENAI_API_KEY": "test_key",
            "VECTOR_STORE_PATH": str(temp_dir / "vectors"),
            "SESSION_STORE_PATH": str(temp_dir / "sessions")
        }

        with patch.dict(os.environ, custom_env, clear=True):
            config = Config()

            assert config.vector_store_path.exists()
            assert config.session_store_path.exists()

    @patch('src.core.config.AsyncOpenAI')
    def test_openai_client_creation(self, mock_openai, temp_dir):
        """Test OpenAI client creation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}, clear=True):
            config = Config()
            client = config.get_openai_client()

            mock_openai.assert_called_once_with(api_key="test_key")

    def test_validate_config_success(self, temp_dir):
        """Test successful configuration validation."""
        # Create conversation data directory
        conversation_dir = temp_dir / "convos"
        conversation_dir.mkdir()

        custom_env = {
            "OPENAI_API_KEY": "test_key",
            "CONVERSATION_DATA_PATH": str(conversation_dir)
        }

        with patch.dict(os.environ, custom_env, clear=True):
            config = Config()
            # Should not raise an exception
            config.validate_config()

    def test_validate_config_missing_api_key(self, temp_dir):
        """Test configuration validation with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()

            with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
                config.validate_config()

    def test_validate_config_missing_conversation_path(self, temp_dir):
        """Test configuration validation with missing conversation path."""
        custom_env = {
            "OPENAI_API_KEY": "test_key",
            "CONVERSATION_DATA_PATH": str(temp_dir / "nonexistent")
        }

        with patch.dict(os.environ, custom_env, clear=True):
            config = Config()

            with pytest.raises(ValueError, match="Conversation data path does not exist"):
                config.validate_config()

    def test_get_openai_client_missing_key(self, temp_dir):
        """Test OpenAI client creation with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()

            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
                config.get_openai_client()
