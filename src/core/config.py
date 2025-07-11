"""
Configuration management for the Alex Persona AI Chatbot.

Handles environment variables, API clients, and application settings
using python-dotenv for Windows compatibility.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI


class Config:
    """Application configuration management."""

    def __init__(self):
        """Initialize configuration by loading environment variables."""
        # Load environment variables from .env file
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(env_path)

        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

        # Storage Paths
        self.vector_store_path = Path(os.getenv("VECTOR_STORE_PATH", "./data/vectors"))
        self.conversation_data_path = Path(os.getenv("CONVERSATION_DATA_PATH", "./convos"))
        self.session_store_path = Path(os.getenv("SESSION_STORE_PATH", "./data/sessions"))

        # Application Settings
        self.max_conversation_history = int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.max_tokens_per_response = int(os.getenv("MAX_TOKENS_PER_RESPONSE", "2000"))

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # Ensure directories exist
        self._create_directories()

    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        self.session_store_path.mkdir(parents=True, exist_ok=True)

    def get_openai_client(self) -> AsyncOpenAI:
        """Get configured OpenAI async client."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        return AsyncOpenAI(api_key=self.openai_api_key)

    def validate_config(self) -> None:
        """Validate that all required configuration is present."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")

        if not self.conversation_data_path.exists():
            raise ValueError(f"Conversation data path does not exist: {self.conversation_data_path}")


# Global configuration instance
config = Config()
