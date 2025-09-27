import React from 'react';
import { Layout } from '../components/layout';
import { ChatInterface } from '../components/chat';

export const Chat: React.FC = () => {
  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Career Chat</h1>
          <p className="text-gray-600 mt-2">
            Get personalized career advice from our AI counselor
          </p>
        </div>

        <ChatInterface />
      </div>
    </Layout>
  );
};