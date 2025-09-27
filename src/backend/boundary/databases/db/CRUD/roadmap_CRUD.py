"""
CRUD operations for CareerRoadmap model.
"""

import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models import CareerRoadmap
from ..engine import get_session_context


class RoadmapCRUD:
    """Simple CRUD operations for career roadmaps"""

    @staticmethod
    def create_roadmap(user_id: str, goal: str, steps: List[Dict], edges: List[Dict], resume_id: Optional[str] = None) -> CareerRoadmap:
        """Create a new career roadmap"""
        with get_session_context() as session:
            roadmap = CareerRoadmap(
                user_id=user_id,
                resume_id=resume_id,
                goal=goal,
                steps_data=json.dumps(steps),
                edges_data=json.dumps(edges)
            )
            session.add(roadmap)
            session.commit()
            session.refresh(roadmap)
            return roadmap

    @staticmethod
    def get_roadmap(roadmap_id: str) -> Optional[CareerRoadmap]:
        """Get roadmap by ID"""
        with get_session_context() as session:
            return session.query(CareerRoadmap).filter(CareerRoadmap.id == roadmap_id).first()

    @staticmethod
    def get_user_roadmaps(user_id: str, limit: int = 10) -> List[CareerRoadmap]:
        """Get user's roadmaps, newest first"""
        with get_session_context() as session:
            return session.query(CareerRoadmap)\
                .filter(CareerRoadmap.user_id == user_id)\
                .order_by(desc(CareerRoadmap.created_at))\
                .limit(limit)\
                .all()

    @staticmethod
    def get_roadmap_data(roadmap_id: str) -> Optional[Dict[str, Any]]:
        """Get roadmap with parsed JSON data"""
        roadmap = RoadmapCRUD.get_roadmap(roadmap_id)
        if not roadmap:
            return None

        return {
            'id': str(roadmap.id),
            'goal': roadmap.goal,
            'steps': json.loads(roadmap.steps_data),
            'edges': json.loads(roadmap.edges_data),
            'created_at': roadmap.created_at
        }

    @staticmethod
    def delete_roadmap(roadmap_id: str, user_id: str) -> bool:
        """Delete roadmap if it belongs to user"""
        with get_session_context() as session:
            roadmap = session.query(CareerRoadmap)\
                .filter(CareerRoadmap.id == roadmap_id, CareerRoadmap.user_id == user_id)\
                .first()

            if roadmap:
                session.delete(roadmap)
                session.commit()
                return True
            return False