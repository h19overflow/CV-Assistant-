"""
Automated section extraction for resume processing.
Runs predefined queries to extract key sections for fast agent access.
"""

import logging
from typing import Dict, List
from langchain_core.documents import Document

from src.backend.core.pipelines.cv_analysis.flow.document_processing_flow import fetch_context
from src.backend.boundary.databases.db.CRUD.resume_CRUD import update_resume

class SectionExtractor:
    """Extracts key resume sections using predefined queries."""

    def __init__(self):
        """Initialize the section extractor."""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Predefined queries for each section
        self.section_queries = {
            "skills": [
                "List programming languages and technologies",
            ],
            "experience": [
                "What work experience is listed?",
            ],
            "projects": [
                "What projects are described?",
            ],
            "education": [
                "List degrees, universities, and academic qualifications",
            ],
            "certificates": [
                "What certifications are listed?",
            ]
        }

    def extract_sections(self, resume_id: str, filename: str, user_id: str) -> Dict[str, str]:
        """
        Extract all sections for a resume using predefined queries.

        Args:
            resume_id: ID of the resume to extract sections for
            filename: Filename to filter queries by
            user_id: ID of the user who owns this resume

        Returns:
            Dict with section names as keys and extracted content as values
        """
        sections = {}

        for section_name, queries in self.section_queries.items():
            try:
                self.logger.info(f"Extracting {section_name} for {filename}")

                # Run queries for this section
                results = fetch_context(queries)

                # Filter results by filename if they have metadata
                filtered_results = []
                for doc in results:
                    if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                        if filename in doc.metadata['source']:
                            filtered_results.append(doc)
                    else:
                        # Include if no metadata filtering possible
                        filtered_results.append(doc)

                # Combine content from all results
                section_content = self._combine_results(filtered_results, section_name)
                sections[section_name] = section_content

                self.logger.info(f"Extracted {len(section_content)} chars for {section_name}")

            except Exception as e:
                self.logger.error(f"Failed to extract {section_name}: {e}")
                sections[section_name] = ""

        # Update the resume record with extracted sections
        try:
            updated_resume = update_resume(
                resume_id=resume_id,
                skills=sections.get("skills", ""),
                experience=sections.get("experience", ""),
                projects=sections.get("projects", ""),
                education=sections.get("education", ""),
                certificates=sections.get("certificates", "")
            )

            if updated_resume:
                self.logger.info(f"Successfully updated resume {resume_id} with extracted sections")
            else:
                self.logger.error(f"Failed to update resume {resume_id}")

        except Exception as e:
            self.logger.error(f"Error updating resume {resume_id}: {e}")

        return sections

    def _combine_results(self, results: List[Document], section_name: str) -> str:
        """
        Combine query results into a single section content.

        Args:
            results: List of Document results
            section_name: Name of the section being extracted

        Returns:
            Combined content string
        """
        if not results:
            return f"No {section_name} information found."

        # Extract content from documents
        content_pieces = []
        for doc in results:
            content = doc.page_content.strip()
            if content and content not in content_pieces:
                content_pieces.append(content)

        # Combine unique content pieces
        combined_content = "\n\n".join(content_pieces)

        # Limit length to avoid extremely long sections
        max_length = 2000
        if len(combined_content) > max_length:
            combined_content = combined_content[:max_length] + "... [content truncated]"

        return combined_content if combined_content else f"No specific {section_name} information found."

    def extract_single_section(self, section_name: str, filename: str) -> str:
        """
        Extract a single section by name.

        Args:
            section_name: Name of section (skills, experience, etc.)
            filename: Filename to filter by

        Returns:
            Extracted section content
        """
        if section_name not in self.section_queries:
            return f"Unknown section: {section_name}"

        queries = self.section_queries[section_name]
        results = fetch_context(queries)

        # Filter by filename
        filtered_results = []
        for doc in results:
            if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                if filename in doc.metadata['source']:
                    filtered_results.append(doc)

        return self._combine_results(filtered_results, section_name)