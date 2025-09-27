import React, { useState, useCallback } from 'react';
import { Upload, File, X } from 'lucide-react';
import { Button, Card } from '../ui';
import { ResumeService } from '../../services';
import toast from 'react-hot-toast';

interface ResumeUploadProps {
  onUploadSuccess?: (resumeId: string, filename: string) => void;
}

export const ResumeUpload: React.FC<ResumeUploadProps> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (isValidFile(file)) {
        setSelectedFile(file);
      }
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (isValidFile(file)) {
        setSelectedFile(file);
      }
    }
  };

  const isValidFile = (file: File) => {
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!validTypes.includes(file.type)) {
      toast.error('Please upload a PDF or Word document');
      return false;
    }

    if (file.size > maxSize) {
      toast.error('File size must be less than 10MB');
      return false;
    }

    return true;
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    try {
      const response = await ResumeService.uploadResume(selectedFile);
      toast.success('Resume uploaded successfully!');
      setSelectedFile(null);
      onUploadSuccess?.(response.resume_id, response.filename);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
  };

  return (
    <Card>
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Resume</h3>

        {!selectedFile ? (
          <div
            className={`border-2 border-dashed rounded-lg p-8 transition-colors ${
              isDragging
                ? 'border-primary-400 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg text-gray-600 mb-2">
              Drag and drop your resume here, or{' '}
              <label className="text-primary-600 hover:text-primary-500 cursor-pointer">
                browse
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileSelect}
                />
              </label>
            </p>
            <p className="text-sm text-gray-500">
              Supports PDF, DOC, DOCX (max 10MB)
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <File className="w-6 h-6 text-gray-400" />
                <div className="text-left">
                  <div className="font-medium text-gray-900">{selectedFile.name}</div>
                  <div className="text-sm text-gray-500">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>
              </div>
              <button
                onClick={clearFile}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex space-x-3">
              <Button onClick={clearFile} variant="outline" className="flex-1">
                Cancel
              </Button>
              <Button onClick={handleUpload} loading={uploading} className="flex-1">
                Upload Resume
              </Button>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};