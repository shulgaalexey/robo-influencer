"""
Base agent architecture for the Robo Influencer system.

Provides abstract base classes and common interfaces for all AI agents
following the Plan/Act pattern from PLANNING.md.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

from ..core.models import ConversationState


class BaseAgent(ABC):
    """Abstract base class for all AI agents in the system."""

    def __init__(self, agent_name: str):
        """
        Initialize the base agent.

        Args:
            agent_name: Unique name for this agent
        """
        self.agent_name = agent_name
        self.created_at = datetime.now()
        self.tools: Dict[str, Any] = {}
        self.state_history: List[ConversationState] = []

    @abstractmethod
    async def process(self, input_state: ConversationState) -> ConversationState:
        """
        Process input state and return updated state.

        Args:
            input_state: Current conversation state

        Returns:
            Updated conversation state
        """
        pass

    @abstractmethod
    async def stream_response(self, query: str) -> AsyncIterator[str]:
        """
        Stream response tokens for real-time interaction.

        Args:
            query: User query

        Yields:
            Response tokens as they are generated
        """
        pass

    def register_tool(self, name: str, tool_function: Any) -> None:
        """
        Register a tool function with the agent.

        Args:
            name: Tool name
            tool_function: Function to register
        """
        self.tools[name] = tool_function

    def get_tool(self, name: str) -> Optional[Any]:
        """
        Get a registered tool by name.

        Args:
            name: Tool name

        Returns:
            Tool function if found, None otherwise
        """
        return self.tools.get(name)

    def log_state(self, state: ConversationState) -> None:
        """
        Log a conversation state for debugging and analysis.

        Args:
            state: Conversation state to log
        """
        self.state_history.append(state)

        # Keep only recent states to prevent memory growth
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-50:]

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about this agent.

        Returns:
            Dictionary with agent metadata
        """
        return {
            "name": self.agent_name,
            "created_at": self.created_at,
            "tools_count": len(self.tools),
            "states_processed": len(self.state_history),
            "last_activity": self.state_history[-1].timestamp if self.state_history else None
        }


class AgenticWorkflow(ABC):
    """Abstract base class for agentic workflows using LangGraph patterns."""

    def __init__(self, workflow_name: str):
        """
        Initialize the workflow.

        Args:
            workflow_name: Unique name for this workflow
        """
        self.workflow_name = workflow_name
        self.nodes: Dict[str, Any] = {}
        self.edges: List[tuple] = []

    @abstractmethod
    def build_graph(self) -> Any:
        """
        Build and compile the LangGraph workflow.

        Returns:
            Compiled workflow graph
        """
        pass

    @abstractmethod
    async def execute(self, initial_state: ConversationState) -> ConversationState:
        """
        Execute the workflow with initial state.

        Args:
            initial_state: Starting conversation state

        Returns:
            Final conversation state after workflow completion
        """
        pass

    def add_node(self, name: str, function: Any) -> None:
        """
        Add a node to the workflow.

        Args:
            name: Node name
            function: Function to execute for this node
        """
        self.nodes[name] = function

    def add_edge(self, from_node: str, to_node: str) -> None:
        """
        Add an edge between workflow nodes.

        Args:
            from_node: Source node name
            to_node: Target node name
        """
        self.edges.append((from_node, to_node))

    def get_workflow_info(self) -> Dict[str, Any]:
        """
        Get information about this workflow.

        Returns:
            Dictionary with workflow metadata
        """
        return {
            "name": self.workflow_name,
            "nodes": list(self.nodes.keys()),
            "edges": self.edges,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges)
        }
