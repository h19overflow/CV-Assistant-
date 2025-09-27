export interface RoadmapStep {
  id: string;
  label: string;
  detail?: string;
  timeframe?: string;
  milestone: boolean;
}

export interface RoadmapEdge {
  source: string;
  target: string;
  label?: string;
}

export interface RoadmapRequest {
  resume_id?: string;
  user_goal: string;
}

export interface RoadmapTextResponse {
  user_goal: string;
  total_steps: number;
  milestones_count: number;
  steps: RoadmapStep[];
  edges: RoadmapEdge[];
  formatted_text: string;
  success: boolean;
}

export interface MermaidResponse {
  user_goal: string;
  mermaid_diagram: string;
  diagram_type: string;
  success: boolean;
}