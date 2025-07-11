"""
Test configuration and fixtures for the Alex Persona AI Chatbot tests.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test_key"
os.environ["LLM_MODEL"] = "gpt-3.5-turbo"
os.environ["EMBEDDING_MODEL"] = "text-embedding-3-small"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = AsyncMock()

    # Mock embeddings response
    client.embeddings.create.return_value.data = [
        Mock(embedding=[0.1, 0.2, 0.3, 0.4, 0.5])
    ]

    # Mock chat completion response
    mock_choice = Mock()
    mock_choice.message.content = "Test response from Alex"
    client.chat.completions.create.return_value.choices = [mock_choice]

    return client


@pytest.fixture
def sample_conversation_content():
    """Sample conversation content for testing."""
    return """# Interview Simulation: Test Conversation

**John (00:00):** Hi Alex, can you tell me about your platform experience?

**Alex (00:30):** Hi John, thanks for having me. I'm an Engineering Manager with over 15 years of experience, primarily focused on leading teams in building AI platforms and enhancing developer experiences. Most recently at Microsoft, I led a team developing AI agent experiences, including a RAG-based platform, which significantly boosted engineer productivity.

What draws me to platform work is the ability to scale impact across thousands of engineers. At Microsoft, we built a platform that served 15,000 engineers and saved over 1,500 engineer-hours weekly through automated assistance and improved workflows.

**John (02:00):** That's impressive. How did you approach the technical architecture?

**Alex (02:30):** The key was designing for extensibility from day one. We implemented what we called the Model Context Protocol (MCP) to allow teams to plug in their own data sources and define contextual understanding for AI agents. This meant the platform wasn't just a monolithic application but a set of services and APIs that other engineering teams could leverage.

The architecture included Azure OpenAI for the LLM backbone, a robust RAG pipeline for context retrieval, and comprehensive APIs for integration with over 150 internal products. We focused on horizontal services that could be reused across different engineering domains.
"""


@pytest.fixture
def sample_conversation_file(temp_dir, sample_conversation_content):
    """Create a sample conversation file for testing."""
    conversation_file = temp_dir / "test_conversation.md"
    conversation_file.write_text(sample_conversation_content)
    return conversation_file
