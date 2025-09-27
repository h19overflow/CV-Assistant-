import React, { useState } from 'react';
import { Route, FileText } from 'lucide-react';
import { Button, Input, Card } from '../ui';
import { MermaidDiagram } from './MermaidDiagram';
import { RoadmapService, ResumeService } from '../../services';
import { Resume, RoadmapTextResponse, MermaidResponse } from '../../types';
import toast from 'react-hot-toast';

interface RoadmapGeneratorProps {
  selectedResumeId?: string;
}

export const RoadmapGenerator: React.FC<RoadmapGeneratorProps> = ({
  selectedResumeId,
}) => {
  const [userGoal, setUserGoal] = useState('');
  const [resumeId, setResumeId] = useState(selectedResumeId || '');
  const [textRoadmap, setTextRoadmap] = useState<RoadmapTextResponse | null>(null);
  const [mermaidRoadmap, setMermaidRoadmap] = useState<MermaidResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'text' | 'diagram'>('text');

  const handleGenerateRoadmap = async () => {
    if (!userGoal.trim()) {
      toast.error('Please enter your career goal');
      return;
    }

    setLoading(true);
    try {
      const request = {
        user_goal: userGoal,
        resume_id: resumeId || undefined,
      };

      // Generate both text and diagram roadmaps
      const [textResponse, diagramResponse] = await Promise.all([
        RoadmapService.generateTextRoadmap(request),
        RoadmapService.generateMermaidRoadmap(request, 'detailed'),
      ]);

      setTextRoadmap(textResponse);
      setMermaidRoadmap(diagramResponse);
      toast.success('Roadmap generated successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate roadmap');
    } finally {
      setLoading(false);
    }
  };

  const renderTextRoadmap = () => {
    if (!textRoadmap) return null;

    return (
      <div className="space-y-6">
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-primary-900 mb-2">
            Career Goal: {textRoadmap.user_goal}
          </h3>
          <div className="flex space-x-4 text-sm text-primary-700">
            <span>{textRoadmap.total_steps} total steps</span>
            <span>{textRoadmap.milestones_count} key milestones</span>
          </div>
        </div>

        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-gray-900">🎯 Key Milestones</h4>
          {textRoadmap.steps
            .filter((step) => step.milestone)
            .map((step) => (
              <Card key={step.id} className="border-l-4 border-yellow-400">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                    <Route className="w-4 h-4 text-yellow-600" />
                  </div>
                  <div className="flex-1">
                    <h5 className="font-semibold text-gray-900">{step.label}</h5>
                    {step.timeframe && (
                      <p className="text-sm text-gray-500 mt-1">⏱️ {step.timeframe}</p>
                    )}
                    {step.detail && (
                      <p className="text-gray-700 mt-2">{step.detail}</p>
                    )}
                  </div>
                </div>
              </Card>
            ))}
        </div>

        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-gray-900">📌 Action Steps</h4>
          {textRoadmap.steps
            .filter((step) => !step.milestone)
            .map((step) => (
              <Card key={step.id} className="border-l-4 border-blue-400">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <FileText className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <h5 className="font-semibold text-gray-900">{step.label}</h5>
                    {step.timeframe && (
                      <p className="text-sm text-gray-500 mt-1">⏱️ {step.timeframe}</p>
                    )}
                    {step.detail && (
                      <p className="text-gray-700 mt-2">{step.detail}</p>
                    )}
                  </div>
                </div>
              </Card>
            ))}
        </div>

        <Card className="bg-gray-50">
          <h4 className="text-lg font-semibold text-gray-900 mb-3">📋 Formatted Roadmap</h4>
          <pre className="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed">
            {textRoadmap.formatted_text}
          </pre>
        </Card>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Generate Career Roadmap
        </h2>

        <div className="space-y-4">
          <Input
            label="Career Goal"
            value={userGoal}
            onChange={(e) => setUserGoal(e.target.value)}
            placeholder="e.g., Become a Senior AI/ML Engineer"
            helperText="Describe your target career position or goal"
          />

          <Button
            onClick={handleGenerateRoadmap}
            loading={loading}
            className="w-full"
            disabled={!userGoal.trim()}
          >
            Generate Roadmap
          </Button>
        </div>
      </Card>

      {(textRoadmap || mermaidRoadmap) && (
        <div className="space-y-4">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('text')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'text'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Text Roadmap
            </button>
            <button
              onClick={() => setActiveTab('diagram')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'diagram'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Visual Diagram
            </button>
          </div>

          {activeTab === 'text' && renderTextRoadmap()}

          {activeTab === 'diagram' && mermaidRoadmap && (
            <Card>
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Visual Roadmap: {mermaidRoadmap.user_goal}
                </h3>
                <p className="text-sm text-gray-600">
                  Interactive diagram showing your career progression path
                </p>
              </div>
              <MermaidDiagram
                diagram={mermaidRoadmap.mermaid_diagram}
                className="bg-white border rounded-lg p-4"
              />
            </Card>
          )}
        </div>
      )}
    </div>
  );
};