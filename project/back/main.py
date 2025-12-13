from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime
from contextlib import asynccontextmanager

# Database imports
from database.postgres_db import get_db, engine, Base
from database.mongo_db import get_mongo_db

# Router imports
from routers.public_api import router as public_router
from routers.admin_api import router as admin_router

# Job scheduler
from jobs.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    Starts/stops the job scheduler
    """
    # Startup
    await start_scheduler()
    yield
    # Shutdown
    await stop_scheduler()


app = FastAPI(
    title="Air Quality Platform API",
    description="Comprehensive API for monitoring and analyzing air quality data. "
                "Includes Public API for citizens/researchers and Admin API for system management.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if not os.getenv("DEBUG", "false").lower() == "true" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(public_router)
app.include_router(admin_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Air Quality API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test PostgreSQL connection
        db.execute("SELECT 1")
        
        # Test MongoDB connection
        mongo_db = await get_mongo_db()
        await mongo_db.command("ping")
        
        return {
            "status": "healthy",
            "postgres": "connected",
            "mongodb": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )

@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Air Quality API",
        "version": "1.0.0",
        "description": "Real-time air quality monitoring and analysis",
        "endpoints": {
            "stations": "/api/stations",
            "readings": "/api/readings",
            "users": "/api/users",
            "alerts": "/api/alerts",
            "reports": "/api/reports"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
