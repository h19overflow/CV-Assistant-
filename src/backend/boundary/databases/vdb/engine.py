from contextlib import contextmanager
from typing import Generator
from langchain_postgres.vectorstores import PGVector
from langchain_huggingface import HuggingFaceEmbeddings # or your preferred embeddings
from langchain_core.documents import Document
import os
from dotenv import load_dotenv
load_dotenv()



class LangchainPgVectorClient:
    def __init__(self, connection_url, collection_name, embedding_model_name="intfloat/e5-large-v2"):
        self.embeddings = HuggingFaceEmbeddings(model=embedding_model_name)
        self.collection_name = collection_name
        self.connection_url = connection_url
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            connection=self.connection_url,
            use_jsonb=True,  # Recommended for metadata
        )

    def insert_documents(self, docs: list, ids=None):
        """
        docs: List of dicts, each with keys 'content', 'metadata' (optional)
        ids: Optional list of string IDs
        """
        documents = [Document(page_content=doc["content"], metadata=doc.get("metadata", {})) for doc in docs]
        self.vector_store.add_documents(documents=documents, ids=ids)

    def query(self, query: str, k=5):
        """
        query: Input text for vector search
        k: Number of top results to return
        """
        results = self.vector_store.similarity_search(query=query, k=k)
        return results
    def get_vs(self):
        return self.vector_store


def get_vector_client(collection_name: str,connection_url: str = os.getenv('POSTGRES_CONNECTION_STRING')) -> Generator[LangchainPgVectorClient, None, None]:
    """Context manager for vector database client"""
    client = LangchainPgVectorClient(connection_url, collection_name)
    return client


