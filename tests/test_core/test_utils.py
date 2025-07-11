"""
Tests for core utilities module.

Tests markdown parsing, speaker identification, and conversation chunking.
"""

from pathlib import Path

import pytest

from src.core.models import ConversationChunk
from src.core.utils import (chunk_text_by_tokens,
                            extract_alex_communication_patterns,
                            is_alex_speaker, load_conversation_files,
                            parse_markdown_conversation)


class TestMarkdownParsing:
    """Test markdown conversation parsing functionality."""

    def test_parse_conversation_success(self, sample_conversation_file):
        """Test successful conversation parsing."""
        chunks = parse_markdown_conversation(sample_conversation_file)

        assert len(chunks) > 0
        assert any(chunk.speaker == "John" for chunk in chunks)
        assert any(chunk.speaker == "Alex" for chunk in chunks)

        # Check Alex's chunks contain expected content
        alex_chunks = [chunk for chunk in chunks if chunk.speaker == "Alex"]
        assert len(alex_chunks) >= 2
        assert any("Microsoft" in chunk.content for chunk in alex_chunks)
        assert any("15,000 engineers" in chunk.content for chunk in alex_chunks)

    def test_parse_nonexistent_file(self, temp_dir):
        """Test parsing non-existent file returns empty list."""
        nonexistent_file = temp_dir / "nonexistent.md"
        chunks = parse_markdown_conversation(nonexistent_file)

        assert chunks == []

    def test_parse_empty_file(self, temp_dir):
        """Test parsing empty file returns empty list."""
        empty_file = temp_dir / "empty.md"
        empty_file.write_text("")
        chunks = parse_markdown_conversation(empty_file)

        assert chunks == []


class TestSpeakerIdentification:
    """Test speaker identification functionality."""

    def test_alex_speaker_variations(self):
        """Test various Alex speaker name formats."""
        alex_variations = [
            "Alex",
            "Alexey",
            "Alex Shulga",
            "Alexey Shulga",
            "alex",
            "ALEX"
        ]

        for variation in alex_variations:
            assert is_alex_speaker(variation), f"Failed to identify {variation} as Alex"

    def test_non_alex_speakers(self):
        """Test non-Alex speakers are not identified as Alex."""
        non_alex_speakers = [
            "John",
            "Mary",
            "Alexander",  # Different name
            "Alex Johnson",  # Different person
            ""
        ]

        for speaker in non_alex_speakers:
            assert not is_alex_speaker(speaker), f"Incorrectly identified {speaker} as Alex"


class TestTextChunking:
    """Test text chunking functionality."""

    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size."""
        text = "This is a short text that should not be chunked."
        chunks = chunk_text_by_tokens(text, chunk_size=100)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_long_text(self):
        """Test chunking long text with overlap."""
        # Create text with 150 words
        words = ["word"] * 150
        text = " ".join(words)

        chunks = chunk_text_by_tokens(text, chunk_size=100, chunk_overlap=20)

        assert len(chunks) > 1
        assert all(len(chunk.split()) <= 100 for chunk in chunks)

    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        words = ["word" + str(i) for i in range(150)]
        text = " ".join(words)

        chunks = chunk_text_by_tokens(text, chunk_size=100, chunk_overlap=20)

        # Check that there's overlap between consecutive chunks
        if len(chunks) > 1:
            first_chunk_words = chunks[0].split()
            second_chunk_words = chunks[1].split()

            # Last 20 words of first chunk should appear in second chunk
            overlap_words = first_chunk_words[-20:]
            assert any(word in second_chunk_words for word in overlap_words)


class TestCommunicationPatterns:
    """Test communication pattern extraction."""

    def test_extract_patterns_from_alex_chunks(self):
        """Test extraction of communication patterns from Alex's responses."""
        alex_chunks = [
            ConversationChunk(
                id="test1",
                speaker="Alex",
                content="I led a team of 15 engineers building a platform that served 60K+ users and saved 1,500 hours weekly through automation.",
                file_source="test.md"
            ),
            ConversationChunk(
                id="test2",
                speaker="Alex",
                content="The platform architecture used Azure OpenAI with a comprehensive RAG pipeline and extensible APIs for horizontal service integration.",
                file_source="test.md"
            ),
            ConversationChunk(
                id="test3",
                speaker="Alex",
                content="My approach focused on collaborative stakeholder engagement and data-driven decision making with clear KPIs.",
                file_source="test.md"
            )
        ]

        patterns = extract_alex_communication_patterns(alex_chunks)

        assert len(patterns) > 0
        assert any("metrics" in pattern.lower() for pattern in patterns)
        assert any("platform" in pattern.lower() for pattern in patterns)
        assert any("leadership" in pattern.lower() or "collaborative" in pattern.lower() for pattern in patterns)


class TestFileLoading:
    """Test conversation file loading functionality."""

    def test_load_conversation_files(self, temp_dir):
        """Test loading conversation files from directory."""
        # Create test markdown files
        (temp_dir / "conversation1.md").write_text("# Test conversation 1")
        (temp_dir / "conversation2.md").write_text("# Test conversation 2")
        (temp_dir / "not_markdown.txt").write_text("Not a markdown file")

        files = load_conversation_files(temp_dir)

        assert len(files) == 2
        assert all(file.suffix == ".md" for file in files)
        assert any(file.name == "conversation1.md" for file in files)
        assert any(file.name == "conversation2.md" for file in files)

    def test_load_from_nonexistent_directory(self, temp_dir):
        """Test loading from non-existent directory returns empty list."""
        nonexistent_dir = temp_dir / "nonexistent"
        files = load_conversation_files(nonexistent_dir)

        assert files == []
