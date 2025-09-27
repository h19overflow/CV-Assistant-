"""
Document processing flow using Prefect for CV analysis pipeline.
Orchestrates document loading, chunking, and vector store insertion.
"""

from prefect import flow
from typing import List
from langchain_core.documents import Document
from src.backend.core.pipelines.cv_analysis.core.document_processor import DocumentProcessor
from datetime import datetime


@flow(name="document-processing-flow")
def document_processing_flow(file_path: str, user_id: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> dict:
    """
    Complete document processing flow using Prefect tasks.

    Args:
        file_path: Path to document file
        user_id: User ID who owns the resume
        model_name: HuggingFace model for embeddings

    Returns:
        Dict with chunks count, resume_id, and sections
    """
    import os
    from src.backend.boundary.databases.db.CRUD.resume_CRUD import create_resume
    from src.backend.core.pipelines.cv_analysis.core.section_extractor import SectionExtractor

    # Get filename
    filename = os.path.basename(file_path)

    # Create resume record first
    resume = create_resume(
        user_id=user_id,
        filename=filename,
        original_text=None  # Will be populated during processing
    )

    # Execute document processing tasks
    processor = DocumentProcessor(model_name=model_name)
    docs = processor.load_document(file_path)
    chunks = processor.chunk_documents(docs)
    processor.insert_to_vector_store(chunks)

    # Auto-extract sections using the created resume_id
    extractor = SectionExtractor()
    sections = extractor.extract_sections(str(resume.id), filename, user_id)

    print(f"Auto-extracted sections for {filename} (user: {user_id}): {list(sections.keys())}")

    return {
        "chunks_processed": len(chunks),
        "resume_id": str(resume.id),
        "sections": sections,
        "filename": filename
    }

def fetch_context(queries:list)->list[Document]:
    from src.backend.boundary.databases.vdb.vdb_engine import get_vector_client
    client = get_vector_client(collection_name='cv_documents')
    # Use the optimized batch query method
    doc_results = client.query_batch(queries, k=5)
    return doc_results

async def fetch_context_async(queries:list)->list[Document]:
    """Async wrapper around sync vector search operations"""
    import asyncio
    return await asyncio.to_thread(fetch_context, queries)

if __name__ == "__main__":
    from src.backend.boundary.databases.vdb.vdb_engine import prewarm_models
    from src.backend.boundary.databases.db.CRUD.auth_CRUD import create_user

    # Create test user
    user = create_user(email='hamzakhaledlklk@gmail.com', password='password123')

    # Process document (automatically creates resume record)
    result = document_processing_flow(
        file_path=r'C:\Users\User\Projects\Resume_System\src\backend\core\pipelines\cv_analysis\core\Hamza_updated.pdf',
        user_id=str(user.id)
    )

    print(f"Processing complete! Resume ID: {result['resume_id']}, Chunks: {result['chunks_processed']}")
    #
    # # Now test performance - should be much faster
    # queries = ["What is the best way to learn Python?"]
    # start_time = datetime.now()
    # results = fetch_context(queries)
    # end_time = datetime.now()
    #
    # for id , r in enumerate(results):
    #     print('results:',id)
    #     print("Content:", r.page_content)
    # print("---"*50)
    # retrieval_time = end_time - start_time
    # print("Retrieval time:", retrieval_time)
    # queries2='What is the best way to learn Python?'
    # start_time = datetime.now()
    # results = fetch_context([queries2])
    # end_time = datetime.now()
    # for id , r in enumerate(results):
    #     print('results:',id)
    #     print("Content:", r.page_content)
    #
    # retrieval_time = end_time - start_time
    # print("Retrieval time:", retrieval_time)
