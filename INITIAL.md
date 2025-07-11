## FEATURE:

- **Alex-Persona AI Chatbot**: A CLI-based conversational AI that mimics Alex's communication style, domain expertise, and preferences by learning from historical conversations and other materials about Alex. Note, Alex's full name is Alexey Shulga.
- **LangGraph Agentic Framework**: Multi-agent workflow system with human-in-the-loop capabilities for sophisticated conversation handling
- **RAG-Powered Context**: Retrieval-Augmented Generation system that searches across all historical conversations stored in `./convos/` folder to provide contextually relevant responses
- **Conversation Memory**: Persistent memory system that maintains context across chat sessions and learns from Alex's conversational patterns
- **OpenAI Integration**: Uses OpenAI's API for LLM capabilities with embeddings for semantic search across conversation history

## EXAMPLES:

In the `examples/` folder, you'll find:

- `examples/cli.py` - CLI interface template for interactive chat sessions
- `examples/agent/` - Best practices for creating LangGraph agents with multiple providers, tool integration, and agent dependencies
- Reference implementations for conversation parsing, persona modeling, and RAG system architecture

**Historical Conversations Format**: See `./convos/` folder for examples of Alex's conversational style and expertise:
- `Alex_fits_Globalization_org_Workday.md` - Demonstrates Alex's technical leadership communication style, AI/platform expertise, and structured thinking approach
- Additional conversation files showing patterns of problem-solving, technical discussions, and domain knowledge

## DOCUMENTATION:

**Core Technologies:**
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - Agent orchestration framework with human-in-the-loop support
- [LangGraph Human-in-the-Loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/) - Interactive workflow management
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/) - Retrieval-Augmented Generation implementation
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings) - Vector embeddings for semantic search
- [LangChain Chatbot Memory](https://python.langchain.com/docs/how_to/chatbots_memory/) - Conversation state management

**Learning Resources:**
- [AI Agents in LangGraph Course](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) - DeepLearning.AI course on agentic workflows
- [Talk Python Episode #507](https://talkpython.fm/episodes/show/507/agentic-ai-workflows-with-langgraph) - Agentic AI Workflows with LangGraph

**Future Enhancement (Next Iteration):**
- Web search integration for knowledge beyond conversation history when Alex cannot answer from existing context

## OTHER CONSIDERATIONS:

**Persona Modeling Requirements:**
- Parse markdown conversations to identify Alex's responses vs. other participants
- Extract communication patterns, technical preferences, and domain expertise areas
- Model decision-making processes and problem-solving approaches
- Capture personality traits, writing style, and preferred technical solutions

**RAG System Specifications:**
- Chunk conversation history into semantically meaningful segments
- Create embeddings for all Alex's responses and relevant context
- Implement similarity search to find relevant historical conversations
- Balance recent conversation priority vs. comprehensive historical search

**LangGraph Architecture:**
- Design agentic workflow for: conversation retrieval → persona analysis → response generation
- Implement human-in-the-loop for response approval/refinement
- Create persistent state management for ongoing conversations
- Plan for future web search agent integration

**Technical Constraints:**
- Work in VSCode on Windows laptop
- Use Powershell
- Use OpenAI API (paid plan available)
- Follow existing project structure and coding standards from `PLANNING.md`
- Implement in Python with proper virtual environment usage
- Create comprehensive unit tests for all components
- Maintain conversation files in markdown format with clear speaker identification

**Data Privacy & Security:**
- Ensure Alex's conversation history remains private and secure
- Implement proper API key management for OpenAI
- Consider conversation data retention and cleanup policies
