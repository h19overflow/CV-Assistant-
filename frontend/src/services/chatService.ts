import api from './api';
import {
  StartSessionRequest,
  StartSessionResponse,
  ChatRequest,
  ChatResponse,
  ChatHistoryResponse,
} from '../types';

export class ChatService {
  static async startSession(request: StartSessionRequest): Promise<StartSessionResponse> {
    const response = await api.post('/career-chat/start-session', request);
    return response.data;
  }

  static async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post('/career-chat/send-message', request);
    return response.data;
  }

  static async getChatHistory(sessionId: string): Promise<ChatHistoryResponse> {
    const response = await api.get(`/career-chat/history/${sessionId}`);
    return response.data;
  }

  static async clearSession(sessionId: string): Promise<{ success: boolean; message: string }> {
    const response = await api.delete(`/career-chat/clear/${sessionId}`);
    return response.data;
  }
}