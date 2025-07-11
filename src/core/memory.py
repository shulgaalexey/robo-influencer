"""
Memory management system for the Alex Persona AI Chatbot.

Handles conversation session persistence, history management, and memory optimization
for maintaining context across chat interactions.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import config
from .models import ChatMessage, ChatSession, PersonaContext


class ConversationMemory:
    """Manages conversation sessions and memory persistence."""

    def __init__(self, session_store_path: Optional[Path] = None):
        """
        Initialize conversation memory manager.

        Args:
            session_store_path: Path to store session files, uses config default if None
        """
        self.session_store_path = session_store_path or config.session_store_path
        self.max_history = config.max_conversation_history

        # Current active session
        self.current_session: Optional[ChatSession] = None

    def create_session(self, session_id: Optional[str] = None) -> ChatSession:
        """
        Create a new chat session.

        Args:
            session_id: Optional session ID, generates UUID if None

        Returns:
            New ChatSession object
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        session = ChatSession(
            session_id=session_id,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.current_session = session
        return session

    def add_message(self, role: str, content: str, context_used: Optional[PersonaContext] = None) -> None:
        """
        Add a message to the current session.

        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
            context_used: Optional RAG context used for the message
        """
        if self.current_session is None:
            self.create_session()

        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            context_used=context_used
        )

        self.current_session.messages.append(message)
        self.current_session.updated_at = datetime.now()

        # Trim history if it exceeds max length
        self._trim_history()

    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation history in format suitable for LLM.

        Args:
            limit: Maximum number of messages to return

        Returns:
            List of message dictionaries with role and content
        """
        if self.current_session is None or not self.current_session.messages:
            return []

        messages = self.current_session.messages
        if limit:
            messages = messages[-limit:]

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    def save_session(self) -> None:
        """Save the current session to disk."""
        if self.current_session is None:
            return

        session_file = self.session_store_path / f"{self.current_session.session_id}.json"

        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_session.model_dump(), f, indent=2, default=str)

        except Exception as e:
            print(f"Error saving session: {e}")

    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Load a session from disk.

        Args:
            session_id: ID of the session to load

        Returns:
            ChatSession object if found, None otherwise
        """
        session_file = self.session_store_path / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            session = ChatSession(**session_data)
            self.current_session = session
            return session

        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def list_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent sessions with metadata.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session metadata dictionaries
        """
        session_files = list(self.session_store_path.glob("*.json"))
        session_info = []

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                info = {
                    "session_id": session_data.get("session_id"),
                    "created_at": session_data.get("created_at"),
                    "updated_at": session_data.get("updated_at"),
                    "message_count": len(session_data.get("messages", [])),
                    "last_message": self._get_last_message_preview(session_data.get("messages", []))
                }
                session_info.append(info)

            except Exception as e:
                print(f"Error reading session file {session_file}: {e}")
                continue

        # Sort by update time, most recent first
        session_info.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

        return session_info[:limit]

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from disk.

        Args:
            session_id: ID of the session to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        session_file = self.session_store_path / f"{session_id}.json"

        try:
            if session_file.exists():
                session_file.unlink()

                # Clear current session if it was deleted
                if self.current_session and self.current_session.session_id == session_id:
                    self.current_session = None

                return True
            return False

        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False

    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up sessions older than specified days.

        Args:
            days_old: Delete sessions older than this many days

        Returns:
            Number of sessions deleted
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        session_files = list(self.session_store_path.glob("*.json"))
        deleted_count = 0

        for session_file in session_files:
            try:
                # Check file modification time
                file_time = datetime.fromtimestamp(session_file.stat().st_mtime)

                if file_time < cutoff_date:
                    session_file.unlink()
                    deleted_count += 1

            except Exception as e:
                print(f"Error processing session file {session_file}: {e}")
                continue

        return deleted_count

    def reset_session(self) -> ChatSession:
        """
        Reset the current session by creating a new one.

        Returns:
            New ChatSession object
        """
        # Save current session before resetting
        if self.current_session:
            self.save_session()

        return self.create_session()

    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary information about the current session.

        Returns:
            Dictionary with session summary information
        """
        if self.current_session is None:
            return {"status": "no_active_session"}

        messages = self.current_session.messages
        user_messages = [msg for msg in messages if msg.role == "user"]
        assistant_messages = [msg for msg in messages if msg.role == "assistant"]

        return {
            "session_id": self.current_session.session_id,
            "created_at": self.current_session.created_at,
            "updated_at": self.current_session.updated_at,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "duration_minutes": self._calculate_session_duration()
        }

    def _trim_history(self) -> None:
        """Trim conversation history to stay within max_history limit."""
        if self.current_session is None:
            return

        if len(self.current_session.messages) > self.max_history:
            # Keep the most recent messages
            self.current_session.messages = self.current_session.messages[-self.max_history:]

    def _get_last_message_preview(self, messages: List[Dict]) -> str:
        """Get a preview of the last message for session listing."""
        if not messages:
            return "No messages"

        last_message = messages[-1]
        content = last_message.get("content", "")

        # Truncate if too long
        if len(content) > 100:
            content = content[:97] + "..."

        return content

    def _calculate_session_duration(self) -> float:
        """Calculate session duration in minutes."""
        if self.current_session is None or not self.current_session.messages:
            return 0.0

        start_time = self.current_session.created_at
        end_time = self.current_session.updated_at

        duration = end_time - start_time
        return duration.total_seconds() / 60.0
