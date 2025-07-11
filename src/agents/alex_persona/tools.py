"""
Tools for Alex Persona AI agent.

Provides RAG retrieval, memory management, and persona analysis tools
for the LangGraph workflow.
"""

from typing import Any, Dict, List, Optional

from ...core.memory import ConversationMemory
from ...core.models import ConversationChunk, PersonaContext
from ...core.rag import ConversationRAG
from .prompts import AlexPersonaPrompts


class RAGRetrievalTool:
    """Tool for retrieving relevant conversation context using RAG."""

    def __init__(self, rag_system: ConversationRAG):
        """
        Initialize RAG retrieval tool.

        Args:
            rag_system: Configured ConversationRAG instance
        """
        self.rag_system = rag_system

    async def retrieve_context(self, query: str, k: int = 5) -> List[ConversationChunk]:
        """
        Retrieve relevant conversation chunks for a query.

        Args:
            query: User query to find context for
            k: Number of chunks to retrieve

        Returns:
            List of relevant ConversationChunk objects
        """
        try:
            chunks = await self.rag_system.similarity_search(query, k=k)
            return chunks
        except Exception as e:
            print(f"Error in RAG retrieval: {e}")
            return []

    async def get_alex_specific_context(self, query: str, k: int = 5) -> List[ConversationChunk]:
        """
        Retrieve context specifically from Alex's responses.

        Args:
            query: User query to find context for
            k: Number of chunks to retrieve

        Returns:
            List of Alex's relevant conversation chunks
        """
        all_chunks = await self.retrieve_context(query, k * 2)  # Get more to filter

        # Filter for Alex's chunks only
        from ...core.utils import is_alex_speaker
        alex_chunks = [chunk for chunk in all_chunks if is_alex_speaker(chunk.speaker)]

        return alex_chunks[:k]


class PersonaAnalysisTool:
    """Tool for analyzing persona context from retrieved conversations."""

    def __init__(self, rag_system: ConversationRAG):
        """
        Initialize persona analysis tool.

        Args:
            rag_system: Configured ConversationRAG instance
        """
        self.rag_system = rag_system

    async def analyze_persona(self, retrieved_chunks: List[ConversationChunk]) -> PersonaContext:
        """
        Analyze retrieved chunks to extract persona characteristics.

        Args:
            retrieved_chunks: Conversation chunks to analyze

        Returns:
            PersonaContext with extracted characteristics
        """
        try:
            persona_context = await self.rag_system.analyze_persona_context(retrieved_chunks)
            return persona_context
        except Exception as e:
            print(f"Error in persona analysis: {e}")
            return PersonaContext()  # Return empty context on error

    def enhance_persona_context(self, persona_context: PersonaContext, query: str) -> PersonaContext:
        """
        Enhance persona context with query-specific insights.

        Args:
            persona_context: Base persona context
            query: Current user query for context

        Returns:
            Enhanced PersonaContext
        """
        query_lower = query.lower()

        # Add query-specific communication style insights
        if any(term in query_lower for term in ['leadership', 'team', 'manage']):
            if "Leadership and team management focus" not in persona_context.communication_style:
                persona_context.communication_style.append("Leadership and team management focus")

        if any(term in query_lower for term in ['technical', 'architecture', 'platform']):
            if "Technical architecture and platform expertise" not in persona_context.communication_style:
                persona_context.communication_style.append("Technical architecture and platform expertise")

        if any(term in query_lower for term in ['ai', 'rag', 'agent', 'llm']):
            if "AI and agentic systems expertise" not in persona_context.technical_expertise:
                persona_context.technical_expertise.append("AI and agentic systems expertise")

        return persona_context


class ConversationMemoryTool:
    """Tool for managing conversation memory and session state."""

    def __init__(self, memory_manager: ConversationMemory):
        """
        Initialize conversation memory tool.

        Args:
            memory_manager: Configured ConversationMemory instance
        """
        self.memory_manager = memory_manager

    def add_user_message(self, content: str) -> None:
        """
        Add user message to conversation memory.

        Args:
            content: User message content
        """
        self.memory_manager.add_message("user", content)

    def add_assistant_message(self, content: str, context_used: Optional[PersonaContext] = None) -> None:
        """
        Add assistant message to conversation memory.

        Args:
            content: Assistant response content
            context_used: Optional persona context used for the response
        """
        self.memory_manager.add_message("assistant", content, context_used)

    def get_conversation_context(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get recent conversation history for context.

        Args:
            limit: Maximum number of messages to return

        Returns:
            List of recent messages in LLM format
        """
        return self.memory_manager.get_conversation_history(limit)

    def save_session(self) -> None:
        """Save current session to persistent storage."""
        self.memory_manager.save_session()

    def reset_conversation(self) -> None:
        """Reset the current conversation session."""
        self.memory_manager.reset_session()

    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session."""
        return self.memory_manager.get_session_summary()


class AlexPersonaToolkit:
    """Comprehensive toolkit for Alex Persona agent operations."""

    def __init__(self, rag_system: ConversationRAG, memory_manager: ConversationMemory):
        """
        Initialize the toolkit with required systems.

        Args:
            rag_system: RAG system for context retrieval
            memory_manager: Memory system for conversation persistence
        """
        self.rag_tool = RAGRetrievalTool(rag_system)
        self.persona_tool = PersonaAnalysisTool(rag_system)
        self.memory_tool = ConversationMemoryTool(memory_manager)
        self.prompts = AlexPersonaPrompts()

    async def prepare_response_context(
        self,
        query: str,
        k_chunks: int = 5
    ) -> Dict[str, Any]:
        """
        Prepare comprehensive context for response generation.

        Args:
            query: User query
            k_chunks: Number of RAG chunks to retrieve

        Returns:
            Dictionary with all context needed for response generation
        """
        try:
            # Retrieve relevant conversation chunks
            retrieved_chunks = await self.rag_tool.get_alex_specific_context(query, k_chunks)

            # Analyze persona context
            persona_context = await self.persona_tool.analyze_persona(retrieved_chunks)
            persona_context = self.persona_tool.enhance_persona_context(persona_context, query)

            # Get conversation history
            conversation_history = self.memory_tool.get_conversation_context()

            # Prepare response prompt
            response_prompt = self.prompts.get_response_generation_prompt(
                query, persona_context, conversation_history
            )

            return {
                "retrieved_chunks": retrieved_chunks,
                "persona_context": persona_context,
                "conversation_history": conversation_history,
                "response_prompt": response_prompt,
                "query": query
            }

        except Exception as e:
            print(f"Error preparing response context: {e}")
            # Return minimal context on error
            return {
                "retrieved_chunks": [],
                "persona_context": PersonaContext(),
                "conversation_history": self.memory_tool.get_conversation_context(),
                "response_prompt": self.prompts.get_error_response_prompt("context_error"),
                "query": query,
                "error": str(e)
            }

    async def validate_and_store_response(
        self,
        query: str,
        response: str,
        persona_context: PersonaContext
    ) -> Dict[str, Any]:
        """
        Validate response quality and store in memory.

        Args:
            query: Original user query
            response: Generated response
            persona_context: Persona context used

        Returns:
            Validation results and storage status
        """
        # Add user message to memory
        self.memory_tool.add_user_message(query)

        # Validate response quality
        validation_results = self.prompts.validate_response_quality(response, persona_context)

        # Add assistant response to memory
        self.memory_tool.add_assistant_message(response, persona_context)

        # Save session
        self.memory_tool.save_session()

        return {
            "validation": validation_results,
            "stored": True,
            "session_info": self.memory_tool.get_session_info()
        }

    def get_conversation_starters(self) -> List[str]:
        """Get suggested conversation starters for the user."""
        return self.prompts.get_conversation_starter_prompts()

    async def handle_error(self, error_type: str, error_details: str) -> str:
        """
        Handle errors gracefully with appropriate Alex-style responses.

        Args:
            error_type: Type of error encountered
            error_details: Specific error details

        Returns:
            Error response in Alex's style
        """
        base_response = self.prompts.get_error_response_prompt(error_type)

        # Add session state to memory for recovery
        self.memory_tool.add_assistant_message(
            f"Error encountered: {base_response}",
            PersonaContext()
        )

        return base_response
