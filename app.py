from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="AI Customs Calculator API",
    description="REST API for customs charge calculation with AI classification",
    version="1.0.0"
)

# Enable CORS (so Streamlit frontend can call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    """API Health Check"""
    return {
        "status": "online",
        "message": "AI Customs Calculator API is running",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "classify": "/api/classify",
            "calculate": "/api/calculate"
        }
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """Check if API is healthy"""
    return {
        "status": "healthy",
        "database": "connected",
        "ml_model": "loaded"
    }

# Test endpoint
@app.get("/api/test")
def test():
    """Simple test endpoint"""
    return {
        "message": "API is working!",
        "timestamp": "2024-02-14"
    }

# Run the API
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )