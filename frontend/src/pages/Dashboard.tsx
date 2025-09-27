import React, { useState, useEffect } from 'react';
import { Upload, FileText, MessageCircle, Route, Plus } from 'lucide-react';
import { Layout } from '../components/layout';
import { Card, Button } from '../components/ui';
import { ResumeService } from '../services';
import { Resume } from '../types';
import toast from 'react-hot-toast';

export const Dashboard: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    try {
      const data = await ResumeService.getUserResumes();
      setResumes(data);
    } catch (error) {
      toast.error('Failed to load resumes');
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      name: 'Total Resumes',
      value: resumes.length,
      icon: FileText,
      color: 'text-blue-600',
    },
    {
      name: 'Chat Sessions',
      value: '0', // TODO: Get from API
      icon: MessageCircle,
      color: 'text-green-600',
    },
    {
      name: 'Roadmaps Generated',
      value: '0', // TODO: Get from API
      icon: Route,
      color: 'text-purple-600',
    },
  ];

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Manage your resumes and track your career progress
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.name} className="text-center">
                <div className="flex items-center justify-center mb-4">
                  <Icon className={`w-8 h-8 ${stat.color}`} />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-600">{stat.name}</div>
              </Card>
            );
          })}
        </div>

        {/* Quick Actions */}
        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button className="flex items-center justify-center space-x-2 h-24">
              <Upload className="w-6 h-6" />
              <span>Upload Resume</span>
            </Button>
            <Button
              variant="outline"
              className="flex items-center justify-center space-x-2 h-24"
            >
              <MessageCircle className="w-6 h-6" />
              <span>Start Chat</span>
            </Button>
            <Button
              variant="outline"
              className="flex items-center justify-center space-x-2 h-24"
            >
              <Route className="w-6 h-6" />
              <span>Generate Roadmap</span>
            </Button>
          </div>
        </Card>

        {/* Recent Resumes */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Resumes</h2>
            <Button size="sm" className="flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Upload New</span>
            </Button>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            </div>
          ) : resumes.length > 0 ? (
            <div className="space-y-3">
              {resumes.slice(0, 5).map((resume) => (
                <div
                  key={resume.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <FileText className="w-5 h-5 text-gray-400" />
                    <div>
                      <div className="font-medium text-gray-900">{resume.filename}</div>
                      <div className="text-sm text-gray-500">
                        Uploaded {new Date(resume.uploaded_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button size="sm" variant="outline">
                      View
                    </Button>
                    <Button size="sm">
                      Generate Feedback
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No resumes uploaded yet</p>
              <Button className="mt-4">
                Upload Your First Resume
              </Button>
            </div>
          )}
        </Card>
      </div>
    </Layout>
  );
};