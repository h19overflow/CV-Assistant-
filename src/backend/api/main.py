"""
Resume System API - Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.api.endpoints.doc_handling.cv_processing import router as cv_router
from src.backend.api.endpoints.authentication.auth_endpoints import router as auth_router

app = FastAPI(
    title="Resume System API",
    description="API for CV analysis and processing",
    version="1.0.0"
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
            "/cv/health": "Health check"
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