"""
Resume System API - Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.api.endpoints.doc_handling.cv_processing import router as cv_router
from src.backend.api.endpoints.authentication.auth_endpoints import router as auth_router
from src.backend.api.endpoints.ai_generation.feedback_endpoints import router as feedback_router
from src.backend.api.endpoints.ai_generation.roadmap_endpoints import router as roadmap_router
from src.backend.api.deps import lifespan_manager

app = FastAPI(
    title="Resume System API",
    description="API for CV analysis and processing",
    version="1.0.0",
    lifespan=lifespan_manager  # Database lifecycle management
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(cv_router)
app.include_router(feedback_router)
app.include_router(roadmap_router)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Resume System API",
        "version": "1.0.0",
        "endpoints": {
            "/auth/register": "Register new user",
            "/auth/login": "Login with email/password",
            "/auth/me": "Get current user info",
            "/auth/verify-token": "Verify JWT token",
            "/cv/upload": "Upload and process CV",
            "/cv/process": "Process existing CV file",
            "/cv/query": "Query CV content",
            "/cv/health": "Health check",
            "/ai/feedback/analyze": "Get AI feedback for latest resume",
            "/ai/feedback/analyze/{resume_id}": "Get AI feedback for specific resume",
            "/ai/roadmap/generate": "Generate career roadmap for latest resume",
            "/ai/roadmap/generate/{resume_id}": "Generate roadmap for specific resume",
            "/ai/roadmap/render/{resume_id}": "Render roadmap as image/file",
            "/ai/roadmap/formats": "Get supported output formats"
        }
    }

@app.get("/health")
async def health():
    """Main health check endpoint."""
    return {"status": "healthy", "service": "resume_system_api"}

# uvicorn src.backend.api.main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)