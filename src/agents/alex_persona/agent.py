"""
Main LangGraph agent for Alex Persona AI chatbot.

Implements the conversational workflow using LangGraph's StateGraph pattern
with nodes for context retrieval, persona analysis, and response generation.
"""

import asyncio
from typing import Any, AsyncIterator, Dict, List, Optional

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from openai import AsyncOpenAI

from ...core.config import config
from ...core.memory import ConversationMemory
from ...core.models import ConversationState, PersonaContext
from ...core.rag import ConversationRAG
from ..base_agent import AgenticWorkflow, BaseAgent
from .prompts import AlexPersonaPrompts
from .tools import AlexPersonaToolkit


class AlexPersonaWorkflow(AgenticWorkflow):
    """LangGraph workflow for Alex Persona conversation processing."""

    def __init__(self, toolkit: AlexPersonaToolkit, openai_client: AsyncOpenAI):
        """
        Initialize the Alex Persona workflow.

        Args:
            toolkit: Alex Persona toolkit with RAG and memory tools
            openai_client: OpenAI client for LLM calls
        """
        super().__init__("alex_persona_workflow")
        self.toolkit = toolkit
        self.client = openai_client
        self.graph: Optional[CompiledStateGraph] = None

        # Build the workflow graph
        self.build_graph()

    def build_graph(self) -> CompiledStateGraph:
        """
        Build and compile the LangGraph workflow.

        Returns:
            Compiled workflow graph
        """
        # Create the state graph
        workflow = StateGraph(ConversationState)

        # Add workflow nodes
        workflow.add_node("retrieve_context", self._retrieve_context_node)
        workflow.add_node("analyze_persona", self._analyze_persona_node)
        workflow.add_node("generate_response", self._generate_response_node)

        # Define workflow edges
        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("retrieve_context", "analyze_persona")
        workflow.add_edge("analyze_persona", "generate_response")
        workflow.set_finish_point("generate_response")

        # Compile the graph
        self.graph = workflow.compile()
        return self.graph

    async def execute(self, initial_state: ConversationState) -> ConversationState:
        """
        Execute the workflow with initial state.

        Args:
            initial_state: Starting conversation state with user query

        Returns:
            Final conversation state with generated response
        """
        if self.graph is None:
            self.build_graph()

        try:
            result = await self.graph.ainvoke(initial_state)
            return result
        except Exception as e:
            # Handle workflow errors gracefully
            error_response = await self.toolkit.handle_error("workflow_error", str(e))
            initial_state.response = error_response
            initial_state.error = str(e)
            return initial_state

    async def _retrieve_context_node(self, state: ConversationState) -> ConversationState:
        """
        Workflow node for retrieving relevant conversation context.

        Args:
            state: Current conversation state

        Returns:
            Updated state with retrieved context
        """
        try:
            # Use query from state or extract from last message
            query = state.query
            if not query and state.messages:
                query = state.messages[-1].get("content", "")

            # Retrieve relevant conversation chunks
            retrieved_chunks = await self.toolkit.rag_tool.get_alex_specific_context(query, k=5)
            state.retrieved_context = retrieved_chunks

            return state

        except Exception as e:
            print(f"Error in retrieve_context_node: {e}")
            state.error = f"Context retrieval error: {str(e)}"
            return state

    async def _analyze_persona_node(self, state: ConversationState) -> ConversationState:
        """
        Workflow node for analyzing persona context from retrieved chunks.

        Args:
            state: Current conversation state with retrieved context

        Returns:
            Updated state with persona analysis
        """
        try:
            # Analyze persona context from retrieved chunks
            persona_context = await self.toolkit.persona_tool.analyze_persona(state.retrieved_context)

            # Enhance with query-specific insights
            query = state.query or (state.messages[-1].get("content", "") if state.messages else "")
            persona_context = self.toolkit.persona_tool.enhance_persona_context(persona_context, query)

            state.persona_analysis = persona_context
            return state

        except Exception as e:
            print(f"Error in analyze_persona_node: {e}")
            state.error = f"Persona analysis error: {str(e)}"
            state.persona_analysis = PersonaContext()  # Empty context on error
            return state

    async def _generate_response_node(self, state: ConversationState) -> ConversationState:
        """
        Workflow node for generating Alex-style response.

        Args:
            state: Current conversation state with context and persona analysis

        Returns:
            Updated state with generated response
        """
        try:
            # Get conversation history for context
            conversation_history = self.toolkit.memory_tool.get_conversation_context(limit=10)

            # Prepare response prompt
            query = state.query or (state.messages[-1].get("content", "") if state.messages else "")
            response_prompt = AlexPersonaPrompts.get_response_generation_prompt(
                query,
                state.persona_analysis or PersonaContext(),
                conversation_history
            )

            # Generate response using OpenAI
            response = await self._call_llm(response_prompt)
            state.response = response

            return state

        except Exception as e:
            print(f"Error in generate_response_node: {e}")
            error_response = AlexPersonaPrompts.get_error_response_prompt("api_error")
            state.response = error_response
            state.error = f"Response generation error: {str(e)}"
            return state

    async def _call_llm(self, prompt: str) -> str:
        """
        Call OpenAI LLM with the prepared prompt.

        Args:
            prompt: System prompt for response generation

        Returns:
            Generated response text
        """
        try:
            response = await self.client.chat.completions.create(
                model=config.llm_model,
                messages=[
                    {"role": "system", "content": AlexPersonaPrompts.get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config.max_tokens_per_response,
                temperature=0.7,
                stream=False
            )

            return response.choices[0].message.content or "I apologize, but I couldn't generate a response right now."

        except Exception as e:
            print(f"Error calling LLM: {e}")
            return AlexPersonaPrompts.get_error_response_prompt("api_error")


class AlexPersonaAgent(BaseAgent):
    """Main Alex Persona AI agent implementing the BaseAgent interface."""

    def __init__(self):
        """Initialize the Alex Persona agent."""
        super().__init__("alex_persona_agent")

        # Initialize core systems
        self.openai_client = config.get_openai_client()
        self.rag_system = ConversationRAG(self.openai_client)
        self.memory_manager = ConversationMemory()

        # Initialize toolkit and workflow
        self.toolkit = AlexPersonaToolkit(self.rag_system, self.memory_manager)
        self.workflow = AlexPersonaWorkflow(self.toolkit, self.openai_client)

        # Agent initialization status
        self.initialized = False

    async def initialize(self, force_rebuild_rag: bool = False) -> None:
        """
        Initialize the agent systems.

        Args:
            force_rebuild_rag: If True, rebuild RAG system from scratch
        """
        if self.initialized:
            return

        print("Initializing Alex Persona agent...")

        # Initialize RAG system
        await self.rag_system.initialize(force_rebuild=force_rebuild_rag)

        # Create initial session if none exists
        if self.memory_manager.current_session is None:
            self.memory_manager.create_session()

        self.initialized = True
        print("Alex Persona agent initialized successfully!")

    async def process(self, input_state: ConversationState) -> ConversationState:
        """
        Process input state through the workflow.

        Args:
            input_state: Input conversation state

        Returns:
            Processed conversation state with response
        """
        if not self.initialized:
            await self.initialize()

        # Execute the workflow
        result_state = await self.workflow.execute(input_state)

        # Log the state for debugging
        self.log_state(result_state)

        return result_state

    async def stream_response(self, query: str) -> AsyncIterator[str]:
        """
        Stream response tokens for real-time interaction.

        Args:
            query: User query

        Yields:
            Response tokens as they are generated
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Prepare context for streaming response
            context = await self.toolkit.prepare_response_context(query)

            # Call OpenAI with streaming
            stream = await self.openai_client.chat.completions.create(
                model=config.llm_model,
                messages=[
                    {"role": "system", "content": AlexPersonaPrompts.get_system_prompt()},
                    {"role": "user", "content": context["response_prompt"]}
                ],
                max_tokens=config.max_tokens_per_response,
                temperature=0.7,
                stream=True
            )

            # Collect full response for memory storage
            full_response = ""

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    yield token

            # Store the complete interaction in memory
            await self.toolkit.validate_and_store_response(
                query, full_response, context.get("persona_context", PersonaContext())
            )

        except Exception as e:
            error_response = await self.toolkit.handle_error("streaming_error", str(e))
            for char in error_response:
                yield char
                await asyncio.sleep(0.01)  # Simulate typing effect

    async def chat_response(self, query: str) -> str:
        """
        Generate a complete response for a user query (non-streaming).

        Args:
            query: User query

        Returns:
            Complete response string
        """
        # Create conversation state
        state = ConversationState(
            messages=[{"role": "user", "content": query}],
            query=query
        )

        # Process through workflow
        result_state = await self.process(state)

        # Validate and store the response
        if result_state.response and not result_state.error:
            await self.toolkit.validate_and_store_response(
                query,
                result_state.response,
                result_state.persona_analysis or PersonaContext()
            )

        return result_state.response or "I apologize, but I couldn't process your request right now."

    def get_conversation_starters(self) -> List[str]:
        """Get suggested conversation starters."""
        return self.toolkit.get_conversation_starters()

    def reset_conversation(self) -> None:
        """Reset the current conversation session."""
        self.toolkit.memory_tool.reset_conversation()

    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information."""
        return self.toolkit.memory_tool.get_session_info()
