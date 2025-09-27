import api from './api';
import { RoadmapRequest, RoadmapTextResponse, MermaidResponse } from '../types';

export class RoadmapService {
  static async generateTextRoadmap(request: RoadmapRequest): Promise<RoadmapTextResponse> {
    const response = await api.post('/ai/roadmap/generate-text', request);
    return response.data;
  }

  static async generateMermaidRoadmap(
    request: RoadmapRequest,
    diagramType: string = 'detailed'
  ): Promise<MermaidResponse> {
    const response = await api.post('/ai/roadmap/generate-mermaid', request, {
      params: { diagram_type: diagramType },
    });
    return response.data;
  }
}