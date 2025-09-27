"""
Chat context manager for loading user resume and roadmap data.
"""

from typing import Dict, Any, List, Optional

from src.backend.core.multi_agent_systems.cv_analysis.road_maps.road_map_agent import get_user_resume_sections
from src.backend.boundary.databases.db.CRUD.roadmap_CRUD import RoadmapCRUD


class ChatContextManager:
    """Manages user context for career chat sessions"""

    def __init__(self):
        pass

    def load_user_context(self, user_id: str, resume_id: Optional[str] = None, roadmap_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Load complete user context for chat session.

        Args:
            user_id: User identifier
            resume_id: Optional specific resume ID
            roadmap_id: Optional specific roadmap ID

        Returns:
            Complete user context dictionary
        """
        context = {
            'user_id': user_id,
            'resume_sections': {},
            'roadmaps': [],
            'current_goal': None
        }

        # Load resume sections
        try:
            resume_sections = get_user_resume_sections(user_id, resume_id)
            if resume_sections:
                context['resume_sections'] = resume_sections
        except Exception as e:
            print(f"Error loading resume sections: {e}")

        # Load roadmaps
        try:
            if roadmap_id:
                # Load specific roadmap
                roadmap_data = RoadmapCRUD.get_roadmap_data(roadmap_id)
                if roadmap_data:
                    context['roadmaps'] = [roadmap_data]
                    context['current_goal'] = roadmap_data['goal']
            else:
                # Load recent roadmaps
                roadmaps = RoadmapCRUD.get_user_roadmaps(user_id, limit=3)
                context['roadmaps'] = []

                for roadmap in roadmaps:
                    roadmap_data = RoadmapCRUD.get_roadmap_data(str(roadmap.id))
                    if roadmap_data:
                        context['roadmaps'].append(roadmap_data)

                # Set current goal from most recent roadmap
                if context['roadmaps']:
                    context['current_goal'] = context['roadmaps'][0]['goal']

        except Exception as e:
            print(f"Error loading roadmaps: {e}")

        return context

    def get_context_summary(self, context: Dict[str, Any]) -> str:
        """
        Create a brief summary of loaded context.

        Args:
            context: User context dictionary

        Returns:
            Human-readable context summary
        """
        summary_parts = []

        # Resume summary
        resume_sections = context.get('resume_sections', {})
        if resume_sections:
            available_sections = [k for k in resume_sections.keys() if k not in ['user_id', 'filename'] and resume_sections[k]]
            if available_sections:
                summary_parts.append(f"Resume sections: {', '.join(available_sections)}")

        # Roadmaps summary
        roadmaps = context.get('roadmaps', [])
        if roadmaps:
            summary_parts.append(f"{len(roadmaps)} career roadmap(s) available")

        # Current goal
        current_goal = context.get('current_goal')
        if current_goal:
            summary_parts.append(f"Current goal: {current_goal}")

        return " | ".join(summary_parts) if summary_parts else "No context available"