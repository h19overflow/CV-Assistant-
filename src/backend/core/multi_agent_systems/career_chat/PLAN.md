# Career Chat Multi-Agent System Implementation Plan

## Overview
This system provides AI-powered career counseling through chat interactions, integrating with user resume data and generated roadmaps for personalized advice.

## Directory Structure
```
src/backend/core/multi_agent_systems/career_chat/
├── __init__.py                    # Package exports
├── PLAN.md                        # This implementation plan
├── career_chat_agent.py           # Main pydantic-ai career counselor agent
├── career_chat_schema.py          # Pydantic request/response models
├── career_chat_prompt.py          # System prompts and templates
├── langchain_wrapper.py           # pydantic-ai ↔ LangChain message bridge
├── chat_context_manager.py       # Resume/roadmap context loading
└── chat_session_manager.py       # Chat session orchestration
```

## Implementation Phases

### Phase 1: Database Integration ✅
- [x] Create directory structure
- [ ] Add CareerRoadmap model to `src/backend/boundary/databases/db/models.py`
- [ ] Create roadmap CRUD operations in `src/backend/boundary/databases/db/CRUD/roadmap_CRUD.py`
- [ ] Leverage existing PostgreSQL connection from engine.py

### Phase 2: Core Multi-Agent System Components
- [ ] **career_chat_agent.py**: pydantic-ai agent with career counseling expertise
- [ ] **career_chat_schema.py**: Request/response models for API integration
- [ ] **career_chat_prompt.py**: System prompts and conversation templates
- [ ] **langchain_wrapper.py**: Convert between pydantic-ai and LangChain message formats
- [ ] **chat_context_manager.py**: Load user resume sections and roadmaps as context
- [ ] **chat_session_manager.py**: Orchestrate chat sessions with context injection

### Phase 3: API Layer Integration
- [ ] Create `src/backend/api/endpoints/career_chat_endpoints.py`
- [ ] Implement FastAPI endpoints that delegate to multi-agent system
- [ ] Ensure clean separation of HTTP concerns vs business logic

### Phase 4: Agent Context Access
The career chat agent will have full access to:
- ✅ Resume data via `get_user_resume_sections()`
- ✅ Saved roadmaps via roadmap CRUD operations
- ✅ Chat history via LangChain PostgresChatMessageHistory
- ✅ Smart context injection for personalized career advice

## Component Responsibilities

### CareerChatAgent
- Main pydantic-ai agent with career counseling capabilities
- Process user messages with full context awareness
- Generate contextual career advice and recommendations
- Reference specific resume sections and roadmap steps

### LangChainWrapper
- Convert user input to HumanMessage format
- Convert agent responses to AIMessage format
- Inject resume/roadmap context as SystemMessage
- Manage conversation flow with PostgresChatMessageHistory

### ChatContextManager
- Load user's resume sections for context
- Retrieve saved roadmaps for reference
- Format context data for agent consumption
- Handle context updates and refresh

### ChatSessionManager
- Orchestrate complete chat sessions
- Initialize sessions with user context
- Manage conversation state and history
- Coordinate between all system components

### API Endpoints
- `POST /career-chat/start-session` - Initialize chat with user context
- `POST /career-chat/send-message` - Process messages through agent
- `GET /career-chat/history/{session_id}` - Retrieve conversation history
- `GET /career-chat/sessions` - List user's active chat sessions

## Integration Benefits
- ✅ Multi-agent system contains all business logic
- ✅ API endpoints are thin HTTP wrappers
- ✅ Agent has comprehensive user context
- ✅ Professional chat persistence via LangChain
- ✅ Maintainable, separation-of-concerns architecture

## Example Usage Flow
1. User calls `POST /career-chat/start-session` with user_id
2. System loads resume data and roadmaps as context
3. LangChain creates chat session with context as SystemMessage
4. User sends message via `POST /career-chat/send-message`
5. System converts to HumanMessage, processes through agent
6. Agent generates contextual response using resume/roadmap data
7. Response converted to AIMessage and stored in chat history
8. User receives personalized career advice with context references

## Technical Stack
- **pydantic-ai**: Advanced agent capabilities and structured outputs
- **LangChain**: Professional chat history persistence
- **PostgreSQL**: Existing database infrastructure
- **FastAPI**: HTTP API layer
- **SQLAlchemy**: Database ORM integration