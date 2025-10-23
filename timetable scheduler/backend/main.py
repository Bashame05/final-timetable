"""
FastAPI application for AI-based college timetable scheduler
Refactored with clean modular architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from routes import (
    timetable_router,
    department_router,
    room_router,
    settings_router
)
from hardcoded_data import (
    HARDCODED_DEPARTMENTS,
    HARDCODED_ROOMS,
    HARDCODED_BATCHES,
    HARDCODED_YEARS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Timetable Scheduler",
    description="Backend API for AI-based college timetable scheduling with OR-Tools CP-SAT solver",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Timetable Scheduler API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "timetable-scheduler",
        "version": "2.0.0"
    }


# Initialize hardcoded data
@app.on_event("startup")
async def startup_event():
    """Initialize hardcoded data on startup"""
    logger.info("Initializing hardcoded data...")
    logger.info(f"Departments: {[d['name'] for d in HARDCODED_DEPARTMENTS]}")
    logger.info(f"Classrooms: C1-C15 (15 total)")
    logger.info(f"Labs: L1-L10 (10 total)")
    logger.info(f"Batches: {HARDCODED_BATCHES}")
    logger.info(f"Years: {list(HARDCODED_YEARS.keys())}")
    logger.info("Hardcoded data initialized successfully!")

# Include routers
app.include_router(timetable_router)
app.include_router(department_router)
app.include_router(room_router)
app.include_router(settings_router)


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting AI Timetable Scheduler Backend...")
    logger.info("Server will be available at: http://localhost:8000")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Press Ctrl+C to stop the server")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
