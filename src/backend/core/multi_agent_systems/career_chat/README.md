# Career Chat Multi-Agent System

AI-powered career counseling with resume and roadmap context integration.

## Quick Start

```python
from src.backend.core.multi_agent_systems.career_chat import ChatSessionManager

# Initialize
manager = ChatSessionManager()

# Start session
session = manager.start_session(user_id="123")
session_id = session['session_id']

# Chat
response = await manager.send_message(session_id, "Should I focus on ML or web dev?", user_id="123")
print(response['agent_response'])
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/career-chat/start-session` | POST | Start new chat with user context |
| `/career-chat/send-message` | POST | Send message, get career advice |
| `/career-chat/history/{session_id}` | GET | Get conversation history |

## Components

- **CareerChatAgent**: pydantic-ai agent with career expertise
- **ChatSessionManager**: Orchestrates sessions with context
- **LangChainWrapper**: Bridges pydantic-ai ↔ LangChain persistence
- **ChatContextManager**: Loads resume/roadmap data

## Database

Uses LangChain's `PostgresChatMessageHistory` for chat persistence and new `CareerRoadmap` model for roadmap storage.

## Features

✅ Context-aware advice using user's resume data
✅ References to specific roadmap steps
✅ Professional chat history persistence
✅ Personalized greetings and follow-ups
✅ Structured responses with suggestions