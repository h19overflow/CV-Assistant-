"""
Application startup script with model pre-warming.
Run this once when your application starts to dramatically improve query performance.
"""

def startup():
    """Initialize and pre-warm all models and connections"""
    from src.backend.boundary.databases.vdb.vdb_engine import prewarm_models

    print("🚀 Starting CV Analysis Pipeline...")

    # Pre-warm with commonly used models
    prewarm_models(models=[
        "sentence-transformers/all-MiniLM-L6-v2"  # Default model
        # Add other models you use here
    ])

    print("✅ Application ready for high-performance queries!")


if __name__ == "__main__":
    startup()