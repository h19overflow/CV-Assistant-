export interface ChatMessage {
  role: 'human' | 'ai' | 'system';
  content: string;
  timestamp: string;
}

export interface StartSessionRequest {
  user_id: string;
  resume_id?: string;
  roadmap_id?: string;
  initial_context?: string;
}

export interface StartSessionResponse {
  session_id: string;
  context_summary: string;
  initial_message: string;
  success: boolean;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  include_context?: boolean;
}

export interface ChatResponse {
  session_id: string;
  agent_response: string;
  context_used: Record<string, any>;
  timestamp: string;
  success: boolean;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessage[];
  total_messages: number;
  session_start: string;
}