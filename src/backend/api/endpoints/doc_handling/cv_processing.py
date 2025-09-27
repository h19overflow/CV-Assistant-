"""
CV processing endpoints for document analysis pipeline
"""

import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from src.backend.core.pipelines.cv_analysis.flow.document_processing_flow import (
    document_processing_flow,
    fetch_context,
    fetch_context_async
)

router = APIRouter(prefix="/cv", tags=["CV Processing"])

class ProcessingResponse(BaseModel):
    """Response model for document processing."""
    success: bool = Field(description="Whether processing was successful")
    message: str = Field(description="Status message")
    chunks_processed: int = Field(description="Number of chunks created")
    file_path: Optional[str] = Field(default=None, description="Path to processed file")

class QueryRequest(BaseModel):
    """Request model for context queries."""
    queries: List[str] = Field(description="List of search queries")
    filename: Optional[str] = Field(default=None, description="Filter by specific CV filename")

class QueryResponse(BaseModel):
    """Response model for context queries."""
    success: bool = Field(description="Whether query was successful")
    results: List[dict] = Field(description="Search results with content and metadata")
    total_results: int = Field(description="Total number of results returned")

@router.post("/process", response_model=ProcessingResponse)
async def upload_and_process_cv(
    file: UploadFile = File(..., description="CV file to process"),
    model_name: str = Form(default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model to use")
):
    """
    Upload and process a CV document through the analysis pipeline.

    Args:
        file: PDF or text file containing the CV
        model_name: HuggingFace model name for embeddings

    Returns:
        ProcessingResponse: Processing status and results
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.txt', '.docx')):
            raise HTTPException(
                status_code=400,
                detail="Only PDF, TXT, and DOCX files are supported"
            )

        # Create temp directory if it doesn't exist
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)

        # Save uploaded file
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process document through the flow
        chunks = document_processing_flow(file_path, model_name)

        return ProcessingResponse(
            success=True,
            message=f"Successfully processed {file.filename}",
            chunks_processed=len(chunks),
            file_path=file_path
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for CV processing service."""
    return {"status": "healthy", "service": "cv_processing"}