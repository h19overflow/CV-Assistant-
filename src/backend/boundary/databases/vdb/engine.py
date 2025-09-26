from contextlib import contextmanager
from typing import Generator
from langchain_postgres.vectorstores import PGVector
from langchain_huggingface import HuggingFaceEmbeddings # or your preferred embeddings
from langchain_core.documents import Document
import os
from dotenv import load_dotenv
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
load_dotenv()



# Global caches to avoid reloading and reconnecting
_embedding_cache = {}
_client_cache = {}
_query_cache = {}  # Cache for query results
_prewarmed = False  # Track if models are prewarmed

class LangchainPgVectorClient:
    def __init__(self, connection_url, collection_name, embedding_model_name="sentence-transformers/all-MiniLM-L6-v2"):
        # Use cached embeddings to avoid reloading
        if embedding_model_name not in _embedding_cache:
            _embedding_cache[embedding_model_name] = HuggingFaceEmbeddings(model=embedding_model_name)

        self.embeddings = _embedding_cache[embedding_model_name]
        self.collection_name = collection_name
        self.connection_url = connection_url
        self.async_connection_url = connection_url.replace("postgresql://", "postgresql+asyncpg://")

        # Lazy initialization for better performance
        self._vector_store = None
        self._async_vector_store = None

    def _ensure_vector_store(self):
        """Lazy initialization of vector store"""
        if self._vector_store is None:
            self._vector_store = PGVector(
                embeddings=self.embeddings,
                collection_name=self.collection_name,
                connection=self.connection_url,
                use_jsonb=True,  # Recommended for metadata
                pre_delete_collection=False,  # Skip deletion check
                create_extension=False,  # Skip extension creation check
            )
        return self._vector_store

    def insert_documents(self, docs: list, ids=None):
        """
        docs: List of dicts, each with keys 'content', 'metadata' (optional)
        ids: Optional list of string IDs
        """
        documents = [Document(page_content=doc["content"], metadata=doc.get("metadata", {})) for doc in docs]
        self._ensure_vector_store().add_documents(documents=documents, ids=ids)

    def query(self, query: str, k=5):
        """
        query: Input text for vector search
        k: Number of top results to return
        """
        # Check cache first
        cache_key = f"{self.collection_name}:{query}:{k}"
        if cache_key in _query_cache:
            return _query_cache[cache_key]

        results = self._ensure_vector_store().similarity_search(query=query, k=k)

        # Cache results for future use
        _query_cache[cache_key] = results
        return results

    def query_batch(self, queries: list, k=5):
        """
        Batch query processing for better performance
        """
        all_results = []
        for query in queries:
            results = self.query(query, k)
            all_results.extend(results)
        return all_results
    def get_vs(self):
        return self._ensure_vector_store()

    async def get_async_vs(self):
        """Get async vector store, creating it if needed"""
        if self._async_vector_store is None:
            # Create async client and get vector store
            async_client = AsyncPGVectorClient(
                embeddings=self.embeddings,
                collection_name=self.collection_name,
                connection_url=self.async_connection_url
            )
            self._async_vector_store = await async_client.get_vector_store()
        return self._async_vector_store


class AsyncPGVectorClient:
    """Separate async-only PGVector client"""

    def __init__(self, embeddings, collection_name, connection_url):
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.connection_url = connection_url
        self._vector_store = None

    async def get_vector_store(self):
        if self._vector_store is None:
            # Create the vector store assuming table already exists
            # This bypasses the sync initialization issue
            self._vector_store = PGVector(
                embeddings=self.embeddings,
                collection_name=self.collection_name,
                connection=self.connection_url,
                use_jsonb=True,
                pre_delete_collection=False,
                create_extension=False  # Skip extension creation
            )

        return self._vector_store


def get_vector_client(collection_name: str, connection_url: str = os.getenv('POSTGRES_CONNECTION_STRING')) -> LangchainPgVectorClient:
    """Get cached vector database client for performance"""
    cache_key = f"{collection_name}:{connection_url}"

    if cache_key not in _client_cache:
        _client_cache[cache_key] = LangchainPgVectorClient(connection_url, collection_name)

    return _client_cache[cache_key]


def prewarm_models(models=None, connection_url=None):
    """
    Pre-warm embedding models and connections at application startup.

    Args:
        models: List of model names to pre-warm. Defaults to common models.
        connection_url: Database connection URL
    """
    global _prewarmed

    if _prewarmed:
        print("Models already pre-warmed, skipping...")
        return

    if models is None:
        models = ["sentence-transformers/all-MiniLM-L6-v2"]

    if connection_url is None:
        connection_url = os.getenv('POSTGRES_CONNECTION_STRING')

    print("🔥 Pre-warming embedding models...")

    for model_name in models:
        print(f"  Loading {model_name}...")
        start_time = __import__('datetime').datetime.now()

        # Load and cache the embedding model
        if model_name not in _embedding_cache:
            _embedding_cache[model_name] = HuggingFaceEmbeddings(model=model_name)
            # Warm up with a dummy embedding
            _embedding_cache[model_name].embed_query("warmup query")

        end_time = __import__('datetime').datetime.now()
        print(f"  ✅ {model_name} loaded in {end_time - start_time}")

    # Pre-warm a default client
    print("🔗 Pre-warming database connection...")
    start_time = __import__('datetime').datetime.now()
    client = get_vector_client("cv_documents", connection_url)
    end_time = __import__('datetime').datetime.now()
    print(f"  ✅ Connection ready in {end_time - start_time}")

    _prewarmed = True
    print("🚀 Pre-warming complete! Subsequent queries will be much faster.")


