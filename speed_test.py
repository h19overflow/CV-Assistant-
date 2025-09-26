"""
Comprehensive speed test for the optimized vector retrieval system
"""
import time
from datetime import datetime
from src.backend.boundary.databases.vdb.engine import prewarm_models
from src.backend.core.pipelines.cv_analysis.flow.document_processing_flow import fetch_context

def test_performance():
    print("🏃 Vector Retrieval Speed Test")
    print("=" * 50)

    # Test queries
    test_queries = [
        ["What programming languages do I know?"],
        ["Where did I study?", "What is my GPA?"],
        ["What machine learning projects have I worked on?"],
        ["What are my technical skills?", "Do I know Python?"],
        ["Tell me about my work experience"]
    ]

    print("\n1️⃣ COLD START (without pre-warming)")
    print("-" * 30)

    # Reset any existing cache to simulate cold start
    from src.backend.boundary.databases.vdb import engine
    engine._embedding_cache.clear()
    engine._client_cache.clear()
    engine._query_cache.clear()
    engine._prewarmed = False

    # Test cold start performance
    start_time = time.time()
    results = fetch_context(["What programming languages do I know?"])
    cold_time = time.time() - start_time

    print(f"Cold start query: {cold_time:.3f} seconds")
    print(f"Results found: {len(results)}")

    print("\n2️⃣ PRE-WARMING PHASE")
    print("-" * 30)

    # Pre-warm the models
    prewarm_start = time.time()
    prewarm_models()
    prewarm_time = time.time() - prewarm_start
    print(f"Pre-warming took: {prewarm_time:.3f} seconds (one-time cost)")

    print("\n3️⃣ HOT PERFORMANCE (after pre-warming)")
    print("-" * 30)

    # Test performance after pre-warming
    times = []

    for i, queries in enumerate(test_queries):
        start_time = time.time()
        results = fetch_context(queries)
        query_time = time.time() - start_time
        times.append(query_time)

        print(f"Test {i+1}: {query_time:.3f}s | {len(queries)} queries → {len(results)} results")

    print("\n📊 PERFORMANCE SUMMARY")
    print("=" * 50)
    print(f"❄️  Cold start time:     {cold_time:.3f}s")
    print(f"🔥 Pre-warming time:     {prewarm_time:.3f}s (one-time)")
    print(f"⚡ Average hot time:     {sum(times)/len(times):.3f}s")
    print(f"🚀 Fastest query:        {min(times):.3f}s")
    print(f"🐌 Slowest query:        {max(times):.3f}s")
    fastest_time = min([t for t in times if t > 0] + [0.001])  # Avoid division by zero
    print(f"📈 Speed improvement:    {cold_time/fastest_time:.1f}x faster")

    print(f"\n✅ After pre-warming, queries are {cold_time/fastest_time:.1f}x faster!")

    # Test repeated queries (should be instant due to caching)
    print("\n4️⃣ CACHE PERFORMANCE TEST")
    print("-" * 30)

    # First run
    start_time = time.time()
    results1 = fetch_context(["What are my skills?"])
    first_run = time.time() - start_time

    # Cached run (same query)
    start_time = time.time()
    results2 = fetch_context(["What are my skills?"])
    cached_run = time.time() - start_time

    print(f"First query:   {first_run:.6f}s")
    print(f"Cached query:  {cached_run:.6f}s")
    print(f"Cache speedup: {first_run/cached_run:.0f}x faster" if cached_run > 0 else "Cache speedup: Nearly instant!")

if __name__ == "__main__":
    test_performance()