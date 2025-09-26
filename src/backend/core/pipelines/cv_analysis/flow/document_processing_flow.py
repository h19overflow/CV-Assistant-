"""
Document processing flow using Prefect for CV analysis pipeline.
Orchestrates document loading, chunking, and vector store insertion.
"""

from prefect import flow
from typing import List
from langchain_core.documents import Document
from src.backend.core.pipelines.cv_analysis.core.document_processor import DocumentProcessor


@flow(name="document-processing-flow")
def document_processing_flow(file_path: str, model_name: str = "intfloat/e5-large-v2") -> List[Document]:
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

if __name__ == "__main__":
    # Example usage
    from src.backend.boundary.databases.vdb.engine import get_vector_client
    vs = get_vector_client(collection_name='cv_documents').get_vs()
    results = vs.similarity_search("What are my skills", k=2)
    for id,r in enumerate(results):
        print(f"Result {id+1}: {r.page_content}\n")

