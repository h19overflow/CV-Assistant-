"""
Document processing pipeline for CV analysis.
Handles PDF loading, semantic chunking, and embedding generation.
Dependencies: langchain-community, langchain-experimental, langchain-huggingface, prefect
"""

import logging
import os
from typing import List
from prefect import task
from langchain_community.document_loaders import PyPDFium2Loader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from src.backend.boundary.databases.vdb.engine import get_vector_client
class DocumentProcessor:
    """
    Processes documents through loading, chunking, and embedding pipeline.
    """

    def __init__(self, model_name: str = "intfloat/e5-large-v2"):
        """
        Initialize document processor with embedding model and chunker.

        Args:
            model_name: HuggingFace model for embeddings
        """
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        try:
            self._embeddings = HuggingFaceEmbeddings(model_name=model_name)
            self._chunker = SemanticChunker(
                embeddings=self._embeddings,
                min_chunk_size=500,
                breakpoint_threshold_amount=0.95,
                breakpoint_threshold_type="percentile"
            )
            self.logger.info(f"Document processor initialized with model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize document processor: {e}")
            raise

    @task(retries=2,description='Loading document from file path',tags=['cv_analysis','loading'])
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load document from file path using PyPDFLoader.

        Args:
            file_path: Path to document file

        Returns:
            List of Document objects

        Raises:
            DocumentLoadError: If document cannot be loaded
        """
        try:
            loader = PyPDFium2Loader(file_path=file_path)
            docs = loader.load()

            self.logger.info(f"Loaded {len(docs)} pages from {file_path}")

            # Debug: Check what we're getting from the loader
            for i, doc in enumerate(docs[:3]):  # Show first 3 docs
                self.logger.info(f"Page {i+1}: length={len(doc.page_content)}, content='{doc.page_content[:100]}...'")

            return docs

        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise DocumentLoadError(f"File not found: {file_path}")
        except Exception as e:
            self.logger.error(f"Error loading document {file_path}: {e}")
            raise DocumentLoadError(f"Failed to load document: {e}")

    @task(retries=2,description='Chunking documents into semantic pieces',tags=['cv_analysis','chunking'])
    def chunk_documents(self, docs: List[Document]) -> List[Document]:
        """
        Split documents into semantic chunks.

        Args:
            docs: List of Document objects to chunk

        Returns:
            List of chunked Document objects

        Raises:
            DocumentChunkError: If chunking fails
        """
        if not docs:
            self.logger.warning("No documents provided for chunking")
            return []

        try:
            chunks_generated = self._chunker.split_documents(docs)
            self.logger.info(f"Created {len(chunks_generated)} chunks from {len(docs)} documents")

            # Debug: Check chunk sizes
            for i, chunk in enumerate(chunks_generated[:5]):  # Show first 5 chunks
                self.logger.info(f"Chunk {i}: length={len(chunk.page_content)}, content='{chunk.page_content[:100]}...'")

            return chunks_generated
        except Exception as e:
            self.logger.error(f"Error chunking documents: {e}")
            raise DocumentChunkError(f"Failed to chunk documents: {e}")

    @task( retries=2,description='Loading document chunks to vector store',tags=['cv_analysis','vector_store'])
    def insert_to_vector_store(self, chunks: List[Document]) -> None:
        """
        Insert document chunks into vector store.

        Args:
            chunks: List of Document chunks to insert

        Raises:
            DocumentEmbedError: If vector insertion fails
        """
        try:
            vector_client = get_vector_client("cv_documents")
            docs_for_insertion = []
            for chunk in chunks:
                docs_for_insertion.append({
                    "content": chunk.page_content,
                    "metadata": chunk.metadata
                })
            vector_client.insert_documents(docs_for_insertion)
            self.logger.info(f"Inserted {len(chunks)} chunks into vector store")
        except Exception as e:
            self.logger.error(f"Error inserting into vector store: {e}")
            raise DocumentEmbedError(f"Failed to insert documents: {e}")

    def process_pipeline(self, file_path: str) -> List[Document]:
        """
        Complete document processing pipeline.

        Args:
            file_path: Path to document file

        Returns:
            List of Document objects ready for vectorstore

        Raises:
            DocumentProcessError: If any pipeline step fails
        """
        try:
            docs = self.load_document(file_path)
            chunks_extracted = self.chunk_documents(docs)
            self.insert_to_vector_store(chunks_extracted)
            return chunks_extracted
        except (DocumentLoadError, DocumentChunkError, DocumentEmbedError) as e:
            raise DocumentProcessError(f"Pipeline failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in pipeline: {e}")
            raise DocumentProcessError(f"Unexpected pipeline error: {e}")


# CUSTOM EXCEPTIONS
class DocumentProcessError(Exception):
    """Base exception for document processing errors."""
    pass

class DocumentLoadError(DocumentProcessError):
    """Error loading document from file."""
    pass

class DocumentChunkError(DocumentProcessError):
    """Error chunking document."""
    pass

class DocumentEmbedError(DocumentProcessError):
    """Error embedding document."""
    pass
if __name__ == "__main__":
    dp = DocumentProcessor()
    chunks = dp.process_pipeline(r"C:\Users\User\Projects\Resume_System\src\backend\core\pipelines\cv_analysis\core\DATABASE-SCHEMA.pdf")

    if not os.path.exists('results'):
        os.mkdir('results')

    with open(r'results\chunks.txt', 'w', encoding='utf-8') as f:
       f.write(str(chunks))