export interface Resume {
  id: string;
  filename: string;
  uploaded_at: string;
  original_text?: string;
  summary?: string;
  skills?: string;
  experience?: string;
  projects?: string;
  education?: string;
  certificates?: string;
}

export interface UploadResponse {
  message: string;
  resume_id: string;
  filename: string;
  success: boolean;
}

export interface FeedbackResponse {
  feedback: string;
  suggestions: string[];
  score: number;
  areas_for_improvement: string[];
  success: boolean;
}