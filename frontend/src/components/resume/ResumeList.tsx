import React, { useState } from 'react';
import { FileText, Download, Trash2, MessageSquare, Route } from 'lucide-react';
import { Button, Card } from '../ui';
import { Resume } from '../../types';
import { ResumeService } from '../../services';
import toast from 'react-hot-toast';

interface ResumeListProps {
  resumes: Resume[];
  onResumeDeleted?: (resumeId: string) => void;
  onGenerateFeedback?: (resumeId: string) => void;
  onGenerateRoadmap?: (resumeId: string) => void;
}

export const ResumeList: React.FC<ResumeListProps> = ({
  resumes,
  onResumeDeleted,
  onGenerateFeedback,
  onGenerateRoadmap,
}) => {
  const [loadingActions, setLoadingActions] = useState<Record<string, boolean>>({});

  const handleDelete = async (resumeId: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    setLoadingActions(prev => ({ ...prev, [`delete-${resumeId}`]: true }));
    try {
      await ResumeService.deleteResume(resumeId);
      toast.success('Resume deleted successfully');
      onResumeDeleted?.(resumeId);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete resume');
    } finally {
      setLoadingActions(prev => ({ ...prev, [`delete-${resumeId}`]: false }));
    }
  };

  const handleGenerateFeedback = async (resumeId: string) => {
    setLoadingActions(prev => ({ ...prev, [`feedback-${resumeId}`]: true }));
    try {
      onGenerateFeedback?.(resumeId);
    } finally {
      setLoadingActions(prev => ({ ...prev, [`feedback-${resumeId}`]: false }));
    }
  };

  const handleGenerateRoadmap = async (resumeId: string) => {
    setLoadingActions(prev => ({ ...prev, [`roadmap-${resumeId}`]: true }));
    try {
      onGenerateRoadmap?.(resumeId);
    } finally {
      setLoadingActions(prev => ({ ...prev, [`roadmap-${resumeId}`]: false }));
    }
  };

  if (resumes.length === 0) {
    return (
      <Card className="text-center py-8">
        <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No resumes yet</h3>
        <p className="text-gray-500 mb-4">Upload your first resume to get started</p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {resumes.map((resume) => (
        <Card key={resume.id} className="hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4 flex-1">
              <div className="flex-shrink-0">
                <FileText className="w-8 h-8 text-primary-600" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-medium text-gray-900 truncate">
                  {resume.filename}
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  Uploaded {new Date(resume.uploaded_at).toLocaleDateString()}
                </p>
                {resume.summary && (
                  <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                    {resume.summary}
                  </p>
                )}
                <div className="flex flex-wrap gap-2 mt-3">
                  {resume.skills && (
                    <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                      Skills Available
                    </span>
                  )}
                  {resume.experience && (
                    <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                      Experience Available
                    </span>
                  )}
                  {resume.education && (
                    <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                      Education Available
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="flex flex-col space-y-2 ml-4">
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleGenerateFeedback(resume.id)}
                  loading={loadingActions[`feedback-${resume.id}`]}
                  className="flex items-center space-x-1"
                >
                  <MessageSquare className="w-4 h-4" />
                  <span>Feedback</span>
                </Button>
                <Button
                  size="sm"
                  onClick={() => handleGenerateRoadmap(resume.id)}
                  loading={loadingActions[`roadmap-${resume.id}`]}
                  className="flex items-center space-x-1"
                >
                  <Route className="w-4 h-4" />
                  <span>Roadmap</span>
                </Button>
              </div>
              <button
                onClick={() => handleDelete(resume.id, resume.filename)}
                disabled={loadingActions[`delete-${resume.id}`]}
                className="text-red-600 hover:text-red-800 text-sm flex items-center space-x-1 self-end"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete</span>
              </button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};