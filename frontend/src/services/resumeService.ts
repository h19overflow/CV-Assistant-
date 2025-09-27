import api from './api';
import { Resume, UploadResponse, FeedbackResponse } from '../types';

export class ResumeService {
  static async uploadResume(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/doc/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  static async getUserResumes(): Promise<Resume[]> {
    const response = await api.get('/doc/resumes');
    return response.data;
  }

  static async getResume(resumeId: string): Promise<Resume> {
    const response = await api.get(`/doc/resume/${resumeId}`);
    return response.data;
  }

  static async deleteResume(resumeId: string): Promise<{ success: boolean }> {
    const response = await api.delete(`/doc/resume/${resumeId}`);
    return response.data;
  }

  static async getResumeFeedback(resumeId: string): Promise<FeedbackResponse> {
    const response = await api.post('/ai/feedback/generate', {
      resume_id: resumeId,
    });
    return response.data;
  }

  static async generateComprehensiveFeedback(resumeId: string): Promise<FeedbackResponse> {
    const response = await api.post('/ai/feedback/comprehensive', {
      resume_id: resumeId,
    });
    return response.data;
  }
}