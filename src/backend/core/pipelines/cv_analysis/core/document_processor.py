"""
Document processing pipeline for CV analysis.
Handles document loading, semantic chunking, and embedding generation.
Dependencies: langchain, huggingface-hub
"""

import logging
from typing import List
from langchain_community.document_loaders import UnstructuredFileIOLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


class DocumentProcessor:
    """
    Processes documents through loading, chunking, and embedding pipeline.
    """

    def __init__(self, model_name: str = "Qwen/Qwen3-Embedding-0.6B"):
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
            self._chunker = SemanticChunker(embeddings=self._embeddings)
            self.logger.info(f"Document processor initialized with model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize document processor: {e}")
            raise

    def load_document(self, file_path: str) -> List[Document]:
        """
        Load document from file path using UnstructuredFileIOLoader.

        Args:
            file_path: Path to document file

        Returns:
            List of Document objects

        Raises:
            DocumentLoadError: If document cannot be loaded
        """
        try:
            with open(file_path, "rb") as f:
                loader = UnstructuredFileIOLoader(
                    f, mode="elements", strategy="fast"
                )
                docs = loader.load()
                self.logger.info(f"Loaded {len(docs)} document elements from {file_path}")
                return docs
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise DocumentLoadError(f"File not found: {file_path}")
        except Exception as e:
            self.logger.error(f"Error loading document {file_path}: {e}")
            raise DocumentLoadError(f"Failed to load document: {e}")

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
            chunks = self._chunker.split_documents(docs)
            self.logger.info(f"Created {len(chunks)} chunks from {len(docs)} documents")
            return chunks
        except Exception as e:
            self.logger.error(f"Error chunking documents: {e}")
            raise DocumentChunkError(f"Failed to chunk documents: {e}")

    def embed_documents(self, docs: List[Document]) -> List[List[float]]:
        """
        Generate embeddings for document chunks.

        Args:
            docs: List of Document objects to embed

        Returns:
            List of embedding vectors

        Raises:
            DocumentEmbedError: If embedding fails
        """
        if not docs:
            self.logger.warning("No documents provided for embedding")
            return []

        try:
            texts = [doc.page_content for doc in docs]
            embeddings = self._embeddings.embed_documents(texts)
            self.logger.info(f"Generated embeddings for {len(docs)} documents")
            return embeddings
        except Exception as e:
            self.logger.error(f"Error embedding documents: {e}")
            raise DocumentEmbedError(f"Failed to embed documents: {e}")

    def process_pipeline(self, file_path: str) -> List[List[float]]:
        """
        Complete document processing pipeline.

        Args:
            file_path: Path to document file

        Returns:
            List of embedding vectors

        Raises:
            DocumentProcessError: If any pipeline step fails
        """
        try:
            docs = self.load_document(file_path)
            chunks = self.chunk_documents(docs)
            embeddings = self.embed_documents(chunks)
            return embeddings
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
    embeddings = dp.process_pipeline(r"C:\Users\User\Projects\Resume_System\src\backend\core\pipelines\cv_analysis\core\DATABASE-SCHEMA.pdf")
    print(embeddings)