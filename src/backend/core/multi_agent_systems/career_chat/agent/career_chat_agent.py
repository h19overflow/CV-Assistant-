"""
Career Chat Agent using pydantic-ai for intelligent career counseling.
"""

import os
from typing import Dict, Any
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel

from .career_chat_schema import CareerAdviceResponse, AgentContextData
from .career_chat_prompt import CAREER_CHAT_SYSTEM_PROMPT, create_context_summary

from dotenv import load_dotenv
load_dotenv()


class CareerChatDeps(BaseModel):
    """Dependencies for the career chat agent"""
    user_context: Dict[str, Any]
    user_message: str


career_chat_agent = Agent(
    model='gemini-2.5-pro',
    output_type=CareerAdviceResponse,
    deps_type=CareerChatDeps,
)


@career_chat_agent.system_prompt
def create_system_prompt(ctx: RunContext[CareerChatDeps]) -> str:
    """Create dynamic system prompt with user context"""
    context_summary = create_context_summary(ctx.deps.user_context)
    return CAREER_CHAT_SYSTEM_PROMPT.format(context_summary=context_summary)


class CareerChatAgent:
    """Main career chat agent for providing personalized career advice"""

    def __init__(self):
        os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

    async def get_career_advice(self, user_message: str, user_context: Dict[str, Any]) -> CareerAdviceResponse:
        """
        Get career advice based on user message and context.

        Args:
            user_message: User's question or message
            user_context: User's resume and roadmap context

        Returns:
            Structured career advice response
        """
        try:
            deps = CareerChatDeps(
                user_context=user_context,
                user_message=user_message
            )

            result = await career_chat_agent.run(
                user_message,
                deps=deps
            )

            return result.output

        except Exception as e:
            # Return fallback response on error
            return CareerAdviceResponse(
                advice=f"I apologize, but I encountered an issue processing your request: {str(e)}. Please try rephrasing your question.",
                references=[],
                suggestions=["Try asking a more specific question about your career goals"],
                confidence=0.0,
                follow_up_questions=["What specific aspect of your career would you like help with?"]
            )