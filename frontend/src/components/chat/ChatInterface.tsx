import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Trash2, RefreshCw } from 'lucide-react';
import { Button, Card } from '../ui';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ChatService } from '../../services';
import { useAuth } from '../../hooks/useAuth';
import { ChatMessage as ChatMessageType } from '../../types';
import toast from 'react-hot-toast';

export const ChatInterface: React.FC = () => {
  const { user } = useAuth();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startNewSession = async () => {
    if (!user) return;

    setInitializing(true);
    try {
      const response = await ChatService.startSession({
        user_id: user.id,
      });

      setSessionId(response.session_id);
      setMessages([
        {
          role: 'system',
          content: response.context_summary,
          timestamp: new Date().toISOString(),
        },
        {
          role: 'ai',
          content: response.initial_message,
          timestamp: new Date().toISOString(),
        },
      ]);

      toast.success('Chat session started!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to start chat session');
    } finally {
      setInitializing(false);
    }
  };

  const sendMessage = async (message: string) => {
    if (!sessionId || !user) return;

    // Add user message immediately
    const userMessage: ChatMessageType = {
      role: 'human',
      content: message,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    setLoading(true);
    try {
      const response = await ChatService.sendMessage({
        session_id: sessionId,
        message,
      });

      // Add AI response
      const aiMessage: ChatMessageType = {
        role: 'ai',
        content: response.agent_response,
        timestamp: response.timestamp || new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to send message');

      // Add error message
      const errorMessage: ChatMessageType = {
        role: 'ai',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearSession = async () => {
    if (!sessionId) return;

    try {
      await ChatService.clearSession(sessionId);
      setSessionId(null);
      setMessages([]);
      toast.success('Chat session cleared');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to clear session');
    }
  };

  const loadChatHistory = async () => {
    if (!sessionId) return;

    try {
      const response = await ChatService.getChatHistory(sessionId);
      setMessages(response.messages);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load chat history');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <Card>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <MessageCircle className="w-6 h-6 text-primary-600" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Career Chat</h2>
              <p className="text-sm text-gray-600">
                Get personalized career advice based on your resume and goals
              </p>
            </div>
          </div>

          <div className="flex space-x-2">
            {sessionId && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadChatHistory}
                  className="flex items-center space-x-1"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Refresh</span>
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearSession}
                  className="flex items-center space-x-1 text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Clear</span>
                </Button>
              </>
            )}
          </div>
        </div>
      </Card>

      {/* Chat Area */}
      <Card className="min-h-[500px] flex flex-col">
        {!sessionId ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-4">
              <MessageCircle className="w-16 h-16 text-gray-300 mx-auto" />
              <div>
                <h3 className="text-lg font-medium text-gray-900">Start a conversation</h3>
                <p className="text-gray-500 mt-1">
                  Begin your career counseling session with our AI advisor
                </p>
              </div>
              <Button
                onClick={startNewSession}
                loading={initializing}
                className="flex items-center space-x-2"
              >
                <MessageCircle className="w-4 h-4" />
                <span>Start Chat Session</span>
              </Button>
            </div>
          </div>
        ) : (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-96">
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg px-4 py-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-gray-200 p-4">
              <ChatInput
                onSendMessage={sendMessage}
                disabled={loading}
                placeholder="Ask me about your career goals, skills development, job search strategies..."
              />
            </div>
          </>
        )}
      </Card>

      {/* Quick Suggestions */}
      {sessionId && messages.length <= 2 && (
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Suggested Questions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              "What skills should I focus on developing next?",
              "How can I improve my resume for better opportunities?",
              "What are the best career paths for my background?",
              "How should I prepare for technical interviews?",
            ].map((suggestion, index) => (
              <button
                key={index}
                onClick={() => sendMessage(suggestion)}
                disabled={loading}
                className="text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <p className="text-sm text-gray-700">{suggestion}</p>
              </button>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};