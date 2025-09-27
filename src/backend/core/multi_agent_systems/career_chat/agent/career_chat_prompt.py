"""
System prompts and templates for Career Chat Agent.
"""

from typing import Dict, Any, List

# Base system prompt for career chat agent
CAREER_CHAT_SYSTEM_PROMPT = """You are an expert career counselor and AI advisor specializing in technology careers, particularly in AI/ML, software engineering, and data science.

Your role is to provide personalized, actionable career advice based on the user's:
- Resume and background information
- Career roadmaps they've generated
- Current goals and aspirations
- Conversation history and context

## Your Expertise:
- Technology career paths and progression
- Skills development and gap analysis
- Industry trends and market insights
- Educational resources and certifications
- Interview preparation and job search strategies
- Career transitions and pivoting

## Communication Style:
- Friendly, supportive, and encouraging
- Specific and actionable advice
- Reference concrete details from their resume and roadmaps
- Ask clarifying questions when needed
- Provide structured recommendations

## Context Available to You:
{context_summary}

## Guidelines:
1. Always reference specific information from the user's resume or roadmaps when relevant
2. Provide actionable, specific advice rather than generic suggestions
3. Consider the user's current level and experience when making recommendations
4. Suggest concrete next steps and resources
5. Be encouraging while being realistic about timelines and challenges
6. Ask follow-up questions to better understand their goals

Remember: You have access to their complete career context, so use it to provide highly personalized advice.
"""

def create_context_summary(user_context: Dict[str, Any]) -> str:
    """
    Create a context summary for the agent prompt.

    Args:
        user_context: Dictionary containing user's resume and roadmap data

    Returns:
        Formatted context summary for agent consumption
    """
    context_parts = []

    # Resume sections summary
    if 'resume_sections' in user_context:
        resume_sections = user_context['resume_sections']
        context_parts.append("## User's Resume Information:")

        for section, content in resume_sections.items():
            if content and section not in ['user_id', 'filename']:
                # Truncate long content for prompt efficiency
                truncated_content = content[:300] + "..." if len(content) > 300 else content
                context_parts.append(f"**{section.title()}**: {truncated_content}")

    # Roadmaps summary
    if 'roadmaps' in user_context and user_context['roadmaps']:
        context_parts.append("\n## User's Career Roadmaps:")

        for i, roadmap in enumerate(user_context['roadmaps'][:3], 1):  # Limit to 3 most recent
            goal = roadmap.get('goal', 'Unknown Goal')
            steps_count = len(roadmap.get('steps', []))
            context_parts.append(f"**Roadmap {i}**: {goal} ({steps_count} steps)")

            # Include key milestones
            if 'steps' in roadmap:
                milestones = [step for step in roadmap['steps'] if step.get('milestone', False)]
                if milestones:
                    milestone_titles = [milestone.get('label', 'Unknown') for milestone in milestones[:3]]
                    context_parts.append(f"  Key milestones: {', '.join(milestone_titles)}")

    # Current goal
    if 'current_goal' in user_context and user_context['current_goal']:
        context_parts.append(f"\n## Current Career Goal:\n{user_context['current_goal']}")

    return "\n".join(context_parts) if context_parts else "No specific context available."

def create_initial_greeting(user_context: Dict[str, Any]) -> str:
    """
    Create a personalized initial greeting message.

    Args:
        user_context: Dictionary containing user's context

    Returns:
        Personalized greeting message
    """
    # Extract user's background for personalization
    resume_sections = user_context.get('resume_sections', {})
    current_goal = user_context.get('current_goal')

    # Determine user's current level/role
    experience = resume_sections.get('experience', '')
    education = resume_sections.get('education', '')

    greeting_parts = [
        "Hello! I'm your AI career counselor, and I'm excited to help you with your career journey. 🚀",
        ""
    ]

    # Personalize based on available information
    if experience:
        greeting_parts.append("I can see you have professional experience, and I've reviewed your background.")
    elif education:
        greeting_parts.append("I've reviewed your educational background and I'm here to help you plan your career path.")
    else:
        greeting_parts.append("I'm here to help you plan and advance your career.")

    if current_goal:
        greeting_parts.append(f"I notice your goal is: {current_goal}")

    greeting_parts.extend([
        "",
        "I can help you with:",
        "• 📋 Analyzing your career roadmaps and next steps",
        "• 🎯 Refining your career goals and strategy",
        "• 📚 Recommending skills, courses, and certifications",
        "• 🔍 Job search and interview preparation advice",
        "• 💡 Industry insights and career transition guidance",
        "",
        "What would you like to discuss about your career? Feel free to ask me anything!"
    ])

    return "\n".join(greeting_parts)

# Follow-up question templates
FOLLOW_UP_QUESTIONS = {
    "skills_development": [
        "What specific skills are you most interested in developing?",
        "Are there any particular technologies or frameworks you'd like to focus on?",
        "What's your preferred learning style - courses, projects, or hands-on experience?"
    ],
    "career_progression": [
        "What's your ideal timeline for reaching your next career milestone?",
        "Are you looking to advance in your current company or explore new opportunities?",
        "What aspects of your target role excite you most?"
    ],
    "job_search": [
        "What type of companies or industries interest you most?",
        "Are you open to remote work or looking for specific locations?",
        "What's your biggest concern about the job search process?"
    ],
    "roadmap_clarification": [
        "Which step in your roadmap would you like to discuss in more detail?",
        "Are there any roadmap steps that seem unclear or challenging?",
        "How do you feel about the timeline in your current roadmap?"
    ]
}

def get_contextual_follow_ups(conversation_context: str, user_context: Dict[str, Any]) -> List[str]:
    """
    Generate contextual follow-up questions based on conversation and user context.

    Args:
        conversation_context: Recent conversation content
        user_context: User's background context

    Returns:
        List of relevant follow-up questions
    """
    # Simple keyword-based selection (could be enhanced with NLP)
    follow_ups = []

    conversation_lower = conversation_context.lower()

    if any(word in conversation_lower for word in ['skill', 'learn', 'course', 'certification']):
        follow_ups.extend(FOLLOW_UP_QUESTIONS['skills_development'][:2])

    if any(word in conversation_lower for word in ['promotion', 'advance', 'senior', 'lead']):
        follow_ups.extend(FOLLOW_UP_QUESTIONS['career_progression'][:2])

    if any(word in conversation_lower for word in ['job', 'interview', 'application', 'hiring']):
        follow_ups.extend(FOLLOW_UP_QUESTIONS['job_search'][:2])

    if any(word in conversation_lower for word in ['roadmap', 'step', 'milestone', 'timeline']):
        follow_ups.extend(FOLLOW_UP_QUESTIONS['roadmap_clarification'][:2])

    # Default questions if no specific context detected
    if not follow_ups:
        follow_ups = [
            "What's your biggest career challenge right now?",
            "Is there a specific aspect of your career you'd like to focus on?"
        ]

    return follow_ups[:3]  # Limit to 3 questions