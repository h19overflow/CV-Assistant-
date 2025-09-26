"""
Quick performance test to isolate bottlenecks
"""
from datetime import datetime
from src.backend.boundary.databases.vdb.engine import get_vector_client

def test_components():
    print("=== Performance Test ===")

    # Test 1: Client creation
    start = datetime.now()
    client = get_vector_client(collection_name='cv_documents')
    end = datetime.now()
    print(f"1. Client creation: {end - start}")

    # Test 2: First embedding
    start = datetime.now()
    client.embeddings.embed_query("test query")
    end = datetime.now()
    print(f"2. First embedding: {end - start}")

    # Test 3: Second embedding (should be faster)
    start = datetime.now()
    client.embeddings.embed_query("another test query")
    end = datetime.now()
    print(f"3. Second embedding: {end - start}")

    # Test 4: Vector search
    start = datetime.now()
    results = client.query("What is the best way to learn Python?", k=2)
    end = datetime.now()
    print(f"4. Vector search: {end - start}")
    print(f"   Found {len(results)} results")

    # Test 5: Cached search
    start = datetime.now()
    results = client.query("What is the best way to learn Python?", k=2)
    end = datetime.now()
    print(f"5. Cached search: {end - start}")

if __name__ == "__main__":
    test_components()