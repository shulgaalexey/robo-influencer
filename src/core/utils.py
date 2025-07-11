"""
Utility functions for the Alex Persona AI Chatbot.

Contains markdown parsing, file handling, and other shared utilities.
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import List

from .models import ConversationChunk


def parse_markdown_conversation(file_path: Path) -> List[ConversationChunk]:
    """
    Parse a markdown conversation file to extract speaker segments.

    Args:
        file_path: Path to the markdown conversation file

    Returns:
        List of ConversationChunk objects representing the conversation
    """
    if not file_path.exists():
        return []

    content = file_path.read_text(encoding='utf-8')
    chunks = []

    # Use findall to match speaker patterns with their content
    # Pattern matches: **Speaker (timestamp):** followed by content until next **speaker or end
    pattern = r'\*\*([A-Za-z]+)\s*\([^)]+\):\*\*\s*(.*?)(?=\n\n\*\*|\Z)'

    matches = re.findall(pattern, content, re.DOTALL)

    for speaker, content_text in matches:
        speaker = speaker.strip()
        content_text = content_text.strip()

        if content_text and not _is_header_or_metadata(content_text):
            chunk_id = _generate_chunk_id(file_path.name, speaker, content_text)

            chunk = ConversationChunk(
                id=chunk_id,
                speaker=speaker,
                content=content_text,
                file_source=file_path.name,
                metadata={
                    "file_path": str(file_path),
                    "parsed_at": datetime.now().isoformat()
                }
            )
            chunks.append(chunk)

    return chunks


def is_alex_speaker(speaker_name: str) -> bool:
    """
    Determine if a speaker name represents Alex Shulga.

    Args:
        speaker_name: The speaker name to check

    Returns:
        True if the speaker is Alex, False otherwise
    """
    speaker_lower = speaker_name.lower().strip()

    # Exact matches for Alex variations
    alex_exact_matches = ['alex', 'alexey', 'alexey shulga', 'alex shulga', 'shulga']

    # Check for exact matches first
    if speaker_lower in alex_exact_matches:
        return True

    # Check for "Alex" or "Alexey" followed by specific last names we know are Alex's
    alex_known_combinations = ['alex shulga', 'alexey shulga']

    return speaker_lower in alex_known_combinations


def chunk_text_by_tokens(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Chunk text into smaller pieces for embedding generation.

    Uses a simple word-based approximation for token counting.

    Args:
        text: Text to chunk
        chunk_size: Maximum tokens per chunk (approximated by words)
        chunk_overlap: Number of tokens to overlap between chunks

    Returns:
        List of text chunks
    """
    words = text.split()

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunks.append(' '.join(chunk_words))

        if end >= len(words):
            break

        start = end - chunk_overlap

    return chunks


def extract_alex_communication_patterns(chunks: List[ConversationChunk]) -> List[str]:
    """
    Extract communication patterns from Alex's conversation chunks.

    Args:
        chunks: List of conversation chunks to analyze

    Returns:
        List of identified communication patterns
    """
    alex_chunks = [chunk for chunk in chunks if is_alex_speaker(chunk.speaker)]

    patterns = []

    # Look for technical depth indicators
    for chunk in alex_chunks:
        content_lower = chunk.content.lower()

        # Technical metrics pattern
        if re.search(r'\d+[k+]?\s*(engineers?|users?|hours?|products?)', content_lower):
            patterns.append("Uses specific metrics and quantifiable impacts")

        # Platform thinking pattern
        if any(term in content_lower for term in ['platform', 'horizontal', 'extensible', 'api', 'service']):
            patterns.append("Demonstrates platform thinking and architectural mindset")

        # Leadership pattern
        if any(term in content_lower for term in ['team', 'led', 'managed', 'mentored', 'collaboration']):
            patterns.append("Shows collaborative leadership and team development focus")

        # AI/Technical expertise pattern
        if any(term in content_lower for term in ['ai', 'rag', 'azure', 'openai', 'agentic', 'llm']):
            patterns.append("Demonstrates deep AI and technical expertise")

    return list(set(patterns))  # Remove duplicates


def _is_header_or_metadata(content: str) -> bool:
    """Check if content is likely a header or metadata, not conversation."""
    content_lower = content.lower().strip()

    # Skip common headers and metadata
    skip_patterns = [
        'interview simulation',
        'date:',
        'role:',
        'interviewer:',
        'candidate:',
        'duration:',
        '---',
        '#',
        'how alex shulga',
        'bottom line:'
    ]

    return any(pattern in content_lower for pattern in skip_patterns)


def _generate_chunk_id(filename: str, speaker: str, content: str) -> str:
    """Generate a unique ID for a conversation chunk."""
    combined = f"{filename}:{speaker}:{content[:100]}"
    return hashlib.md5(combined.encode()).hexdigest()[:12]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for Windows compatibility.

    Args:
        filename: Original filename

    Returns:
        Windows-compatible filename
    """
    # Remove or replace invalid Windows filename characters
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    return filename.strip()


def load_conversation_files(conversation_path: Path) -> List[Path]:
    """
    Load all markdown conversation files from a directory.

    Args:
        conversation_path: Path to directory containing conversation files

    Returns:
        List of Path objects for conversation files
    """
    if not conversation_path.exists():
        return []

    return list(conversation_path.glob("*.md"))
