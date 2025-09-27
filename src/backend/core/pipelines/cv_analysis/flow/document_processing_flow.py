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
def document_processing_flow(file_path: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                           resume_id: str = None, user_id: str = None) -> List[Document]:
    """
    Complete document processing flow using Prefect tasks.

    Args:
        file_path: Path to document file
        model_name: HuggingFace model for embeddings
        resume_id: Optional resume ID for automatic section extraction
        user_id: Optional user ID who owns the resume

    Returns:
        List of processed Document chunks
    """
    import os
    processor = DocumentProcessor(model_name=model_name)

    # Execute tasks in sequence
    docs = processor.load_document(file_path)
    chunks = processor.chunk_documents(docs)
    processor.insert_to_vector_store(chunks)

    # Auto-extract sections if resume_id and user_id provided
    if resume_id and user_id:
        from src.backend.core.pipelines.cv_analysis.core.section_extractor import SectionExtractor

        filename = os.path.basename(file_path)
        extractor = SectionExtractor()
        sections = extractor.extract_sections(resume_id, filename, user_id)
        print(f"Auto-extracted sections for {filename} (user: {user_id}): {list(sections.keys())}")

    return chunks

def fetch_context(queries:list)->list[Document]:
    from src.backend.boundary.databases.vdb.vdb_engine import get_vector_client
    client = get_vector_client(collection_name='cv_documents')
    # Use the optimized batch query method
    doc_results = client.query_batch(queries, k=1)
    return doc_results

async def fetch_context_async(queries:list)->list[Document]:
    """Async wrapper around sync vector search operations"""
    import asyncio
    return await asyncio.to_thread(fetch_context, queries)

if __name__ == "__main__":
    from src.backend.boundary.databases.vdb.vdb_engine import prewarm_models
    from src.backend.boundary.databases.db.CRUD.auth_CRUD import AuthCRUD
    user = AuthCRUD.create_user(email='hamzakhaledlklk@gmail.com', password='password123')

    processing_response  = document_processing_flow(
    file_path=r'C:\Users\User\Projects\Resume_System\src\backend\core\pipelines\cv_analysis\core\Hamza_updated.pdf',
        user_id=user.id,
        resume_id=user.id,
    )
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
