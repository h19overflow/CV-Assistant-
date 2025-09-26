from langchain_postgres.vectorstores import PGVector
from langchain_huggingface import HuggingFaceEmbeddings # or your preferred embeddings
from langchain_core.documents import Document

class LangchainPgVectorClient:
    def __init__(self, connection_url, collection_name, embedding_model_name="google/embeddinggemma-300m"):
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
if __name__ == "__main__":
    client = LangchainPgVectorClient(connection_url="postgresql://postgres:postgres@localhost:6024/postgres", collection_name="test")
    # docs = [
    #     {"content": "This is a test document", "metadata": {"source": "test"}},
    #     {"content": "This is another test document", "metadata": {"source": "test"}},
    # ]
    # client.insert_documents(docs)
