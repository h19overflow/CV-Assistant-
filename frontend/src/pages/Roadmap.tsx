import React from 'react';
import { Layout } from '../components/layout';
import { RoadmapGenerator } from '../components/roadmap';

export const Roadmap: React.FC = () => {
  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Career Roadmap</h1>
          <p className="text-gray-600 mt-2">
            Generate a personalized career roadmap based on your resume and goals
          </p>
        </div>

        <RoadmapGenerator />
      </div>
    </Layout>
  );
};