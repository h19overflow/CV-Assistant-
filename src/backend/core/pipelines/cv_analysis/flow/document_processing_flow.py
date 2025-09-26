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
def document_processing_flow(file_path: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[Document]:
    """
    Complete document processing flow using Prefect tasks.

    Args:
        file_path: Path to document file
        model_name: HuggingFace model for embeddings

    Returns:
        List of processed Document chunks
    """
    processor = DocumentProcessor(model_name=model_name)

    # Execute tasks in sequence
    docs = processor.load_document(file_path)
    chunks = processor.chunk_documents(docs)
    processor.insert_to_vector_store(chunks)

    return chunks

def fetch_context(queries:list)->list[Document]:
    from src.backend.boundary.databases.vdb.engine import get_vector_client
    client = get_vector_client(collection_name='cv_documents')
    # Use the optimized batch query method
    doc_results = client.query_batch(queries, k=2)
    return doc_results

async def fetch_context_async(queries:list)->list[Document]:
    """Async wrapper around sync vector search operations"""
    import asyncio
    return await asyncio.to_thread(fetch_context, queries)

if __name__ == "__main__":
    from src.backend.boundary.databases.vdb.engine import prewarm_models

    # Pre-warm models at startup
    prewarm_models()

    # Now test performance - should be much faster
    queries = ["What is the best way to learn Python?"]
    start_time = datetime.now()
    results = fetch_context(queries)
    end_time = datetime.now()

    for id , r in enumerate(results):
        print('results:',id)
        print("Content:", r.page_content)
    print("---"*50)
    retrieval_time = end_time - start_time
    print("Retrieval time:", retrieval_time)
    queries2='What is the best way to learn Python?'
    start_time = datetime.now()
    results = fetch_context([queries2])
    end_time = datetime.now()
    for id , r in enumerate(results):
        print('results:',id)
        print("Content:", r.page_content)

    retrieval_time = end_time - start_time
    print("Retrieval time:", retrieval_time)
