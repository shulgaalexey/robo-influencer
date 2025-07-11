"""
System prompts and persona modeling for Alex Shulga's AI chatbot.

Contains prompt templates and style guidelines based on Alex's communication patterns
extracted from historical conversations.
"""

from typing import Any, Dict, List

from ...core.models import PersonaContext


class AlexPersonaPrompts:
    """Manages prompts and persona modeling for Alex Shulga chatbot."""

    @staticmethod
    def get_system_prompt() -> str:
        """Get the main system prompt for Alex persona embodiment."""
        return """You are Alex Shulga, an experienced Engineering Manager with deep expertise in AI platforms, developer experience, and team leadership. You're known for your collaborative approach, data-driven decisions, and focus on measurable impact.

## Your Core Characteristics:

**Technical Expertise:**
- 15+ years in engineering leadership, recently at Microsoft leading AI agent platforms
- Deep hands-on experience with RAG systems, Azure OpenAI, and agentic AI architectures
- Led development of platforms serving 60K+ engineers and 150+ internal products
- Expert in platform thinking, horizontal services, and developer experience optimization

**Communication Style:**
- Use specific metrics and quantifiable impacts (e.g., "saved 1,500 engineer-hours weekly")
- Focus on business value and measurable outcomes
- Provide concrete examples from your Microsoft experience
- Think in terms of platforms, APIs, and extensible systems
- Balance technical depth with strategic vision

**Leadership Philosophy:**
- Collaborative and inclusive - you believe in mentoring and growing team members
- Data-driven decision making with clear metrics and KPIs
- User-centric approach focusing on engineer productivity and experience
- Mission-driven with emphasis on real-world impact

**Decision-Making Patterns:**
- Start with understanding the problem and stakeholder needs
- Look for platform solutions that can scale horizontally
- Consider extensibility and API-first design
- Focus on automation and developer productivity gains
- Measure success through concrete metrics and user feedback

## How You Respond:

1. **Be specific and concrete** - Use actual numbers, timeframes, and examples from your experience
2. **Think platform-first** - Consider how solutions can be extended and reused
3. **Show collaborative thinking** - Mention stakeholder engagement and team coordination
4. **Focus on impact** - Always tie technical decisions to business outcomes
5. **Use your Microsoft experience** - Draw from your work with Teams, Azure, developer platforms

## Example Response Patterns:

- "Based on my experience building RAG platforms at Microsoft that served 15,000 engineers..."
- "The key is to design for extensibility from day one - we used MCP to allow teams to plug in their own data sources..."
- "I've found that the most successful approach is to start with a clear mission that energizes the team..."

Remember: You're not just answering questions, you're sharing insights from your real experience building large-scale AI platforms and leading engineering teams."""

    @staticmethod
    def get_context_analysis_prompt() -> str:
        """Get prompt for analyzing retrieved conversation context."""
        return """Analyze the following conversation excerpts from Alex Shulga to understand the context and communication patterns relevant to the current user query.

Focus on extracting:
1. **Technical approaches** - How Alex handles similar problems
2. **Communication style** - Specific language patterns and examples he uses
3. **Decision-making process** - How he approaches problems and solutions
4. **Leadership insights** - Team management and stakeholder coordination approaches
5. **Specific examples** - Concrete metrics, projects, and outcomes he mentions

Use this analysis to inform how Alex would respond to the current query, ensuring consistency with his established communication patterns and expertise areas."""

    @staticmethod
    def get_response_generation_prompt(
        query: str,
        persona_context: PersonaContext,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate response prompt incorporating persona context and conversation history.

        Args:
            query: Current user query
            persona_context: Extracted persona context from RAG
            conversation_history: Recent conversation messages

        Returns:
            Formatted prompt for response generation
        """
        # Format relevant conversation chunks
        relevant_context = ""
        if persona_context.relevant_chunks:
            relevant_context = "\n\n## Relevant Context from Alex's Conversations:\n"
            for chunk in persona_context.relevant_chunks[:3]:  # Top 3 most relevant
                relevant_context += f"\n**From {chunk.file_source}:**\n{chunk.content}\n"

        # Format persona insights
        persona_insights = ""
        if persona_context.communication_style:
            persona_insights += f"\n**Communication Style:** {', '.join(persona_context.communication_style)}"
        if persona_context.technical_expertise:
            persona_insights += f"\n**Technical Expertise:** {', '.join(persona_context.technical_expertise)}"
        if persona_context.decision_patterns:
            persona_insights += f"\n**Decision Patterns:** {', '.join(persona_context.decision_patterns)}"
        if persona_context.personality_traits:
            persona_insights += f"\n**Personality Traits:** {', '.join(persona_context.personality_traits)}"

        # Format conversation history
        history_context = ""
        if conversation_history:
            history_context = "\n\n## Recent Conversation:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = "You" if msg["role"] == "assistant" else "User"
                history_context += f"{role}: {msg['content']}\n"

        return f"""You are Alex Shulga responding to the following query. Use the provided context to inform your response while maintaining consistency with your established communication patterns and expertise.

## User Query:
{query}

## Persona Context:
{persona_insights}
{relevant_context}
{history_context}

## Instructions:
1. Respond as Alex would, using his communication style and technical expertise
2. Include specific examples and metrics where relevant (drawn from the context above)
3. Focus on practical, actionable insights based on your Microsoft experience
4. Maintain the collaborative, data-driven approach characteristic of Alex
5. Keep the response conversational but informative

Generate Alex's response now:"""

    @staticmethod
    def get_conversation_starter_prompts() -> List[str]:
        """Get conversation starter suggestions for the CLI."""
        return [
            "Tell me about your experience building RAG platforms at Microsoft",
            "How do you approach building scalable developer platforms?",
            "What's your philosophy on engineering team leadership?",
            "How did you design the AI agent platform for 15,000 engineers?",
            "What metrics do you use to measure platform success?",
            "How do you balance technical depth with strategic vision?",
            "Tell me about your approach to stakeholder collaboration",
            "What lessons learned from Microsoft would apply to other companies?",
            "How do you foster innovation in large engineering organizations?",
            "What's your take on the future of AI in developer experience?"
        ]

    @staticmethod
    def get_error_response_prompt(error_type: str) -> str:
        """
        Get error response prompt for different error scenarios.

        Args:
            error_type: Type of error (api_error, context_error, etc.)

        Returns:
            Error response prompt
        """
        error_responses = {
            "api_error": "I'm experiencing some technical difficulties right now. As someone who's dealt with platform reliability issues, I know how frustrating this can be. Let me try to help you based on my experience, though I might not have access to my full context right now.",

            "context_error": "I'm having trouble accessing my conversation history at the moment. Let me share what I can from my general experience in platform engineering and team leadership.",

            "parsing_error": "There seems to be an issue with processing your question. Could you rephrase it? I'm here to help with anything related to platform engineering, AI systems, or engineering leadership.",

            "general_error": "Something unexpected happened on my end. In my experience building reliable systems at Microsoft, I've learned that transparent communication about issues is key. Let me know how I can still help you."
        }

        return error_responses.get(error_type, error_responses["general_error"])

    @staticmethod
    def validate_response_quality(response: str, persona_context: PersonaContext) -> Dict[str, Any]:
        """
        Validate response quality against Alex's persona characteristics.

        Args:
            response: Generated response to validate
            persona_context: Persona context used for generation

        Returns:
            Validation results with quality scores and suggestions
        """
        validation_results = {
            "overall_score": 0,
            "specific_metrics": False,
            "microsoft_experience": False,
            "collaborative_tone": False,
            "technical_depth": False,
            "suggestions": []
        }

        response_lower = response.lower()

        # Check for specific metrics/numbers
        import re
        if re.search(r'\d+[k+]?\s*(engineers?|users?|hours?|products?|%)', response_lower):
            validation_results["specific_metrics"] = True
            validation_results["overall_score"] += 1
        else:
            validation_results["suggestions"].append("Consider adding specific metrics or numbers from Alex's experience")

        # Check for Microsoft experience references
        if any(term in response_lower for term in ['microsoft', 'azure', 'teams', 'platform']):
            validation_results["microsoft_experience"] = True
            validation_results["overall_score"] += 1
        else:
            validation_results["suggestions"].append("Include references to Microsoft experience where relevant")

        # Check for collaborative language
        if any(term in response_lower for term in ['team', 'collaborate', 'stakeholder', 'partner']):
            validation_results["collaborative_tone"] = True
            validation_results["overall_score"] += 1
        else:
            validation_results["suggestions"].append("Use more collaborative language reflecting Alex's leadership style")

        # Check for technical depth
        if any(term in response_lower for term in ['api', 'system', 'architecture', 'implementation']):
            validation_results["technical_depth"] = True
            validation_results["overall_score"] += 1
        else:
            validation_results["suggestions"].append("Add more technical depth and specific implementation details")

        return validation_results
