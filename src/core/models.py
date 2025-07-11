"""
Core data models for the Alex Persona AI Chatbot.

This module defines the Pydantic models used throughout the application
for type safety and data validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConversationChunk(BaseModel):
    """Represents a semantically meaningful conversation segment."""

    id: str = Field(..., description="Unique identifier for the chunk")
    speaker: str = Field(..., description="Speaker name (Alex, John, etc.)")
    content: str = Field(..., description="Actual conversation content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    timestamp: Optional[datetime] = Field(None, description="When this was said")
    file_source: str = Field(..., description="Source conversation file")
    embedding: Optional[List[float]] = Field(None, description="OpenAI embedding vector")


class PersonaContext(BaseModel):
    """Captures Alex's persona elements from retrieved conversations."""

    communication_style: List[str] = Field(default_factory=list)
    technical_expertise: List[str] = Field(default_factory=list)
    decision_patterns: List[str] = Field(default_factory=list)
    personality_traits: List[str] = Field(default_factory=list)
    relevant_chunks: List[ConversationChunk] = Field(default_factory=list)


class ChatMessage(BaseModel):
    """Single message in ongoing conversation."""

    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    context_used: Optional[PersonaContext] = Field(None, description="RAG context")


class ChatSession(BaseModel):
    """Complete chat session with memory."""

    session_id: str = Field(..., description="Unique session identifier")
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ConversationState(BaseModel):
    """LangGraph state for conversation workflow."""

    messages: List[Dict[str, str]] = Field(default_factory=list)
    query: str = Field("", description="Current user query")
    retrieved_context: List[ConversationChunk] = Field(default_factory=list)
    persona_analysis: Optional[PersonaContext] = Field(None)
    response: str = Field("", description="Generated response")
    error: Optional[str] = Field(None, description="Error message if any")
