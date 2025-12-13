"""
Admin REST API Router
Provides administrative functionality for system management
Requires admin role authentication
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database.postgres_db import get_db
from models import (
    Provider, Station, AppUser, Role, Permission, 
    AirQualityReading, Alert, Report
)
from schemas import StationCreate, StationResponse, UserResponse, UserCreate, UserUpdate
from jobs.scheduler import scheduler

router = APIRouter(prefix="/admin", tags=["admin"])


# =====================================================
# SYSTEM MONITORING
# =====================================================

@router.get("/health")
def system_health(db: Session = Depends(get_db)):
    """
    Comprehensive system health check
    Returns status of all components
    """
    from sqlalchemy import text
    
    health = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy",
        "components": {}
    }
    
    # Check PostgreSQL
    try:
        db.execute(text("SELECT 1"))
        health["components"]["postgresql"] = {"status": "up", "message": "Connected"}
    except Exception as e:
        health["components"]["postgresql"] = {"status": "down", "error": str(e)}
        health["status"] = "degraded"
    
    # Check MongoDB (from logs collection)
    try:
        from database.mongo_db import get_mongo_db
        import asyncio
        mongo_db = asyncio.run(get_mongo_db())
        asyncio.run(mongo_db.command("ping"))
        health["components"]["mongodb"] = {"status": "up", "message": "Connected"}
    except Exception as e:
        health["components"]["mongodb"] = {"status": "down", "error": str(e)}
        health["status"] = "degraded"
    
    # Check scheduled jobs
    try:
        job_status = scheduler.get_job_status()
        health["components"]["scheduler"] = {
            "status": "up",
            "jobs": job_status
        }
    except Exception as e:
        health["components"]["scheduler"] = {"status": "down", "error": str(e)}
    
    # Database statistics
    try:
        stats = {
            "stations": db.query(Station).count(),
            "users": db.query(AppUser).count(),
            "alerts": db.query(Alert).filter(Alert.is_active == True).count(),
            "readings_24h": db.query(AirQualityReading).filter(
                AirQualityReading.datetime >= datetime.utcnow() - timedelta(hours=24)
            ).count(),
        }
        health["database_stats"] = stats
    except Exception as e:
        health["database_stats"] = {"error": str(e)}
    
    return health


@router.get("/stats")
def system_statistics(db: Session = Depends(get_db)):
    """
    System-wide statistics
    Total counts, recent activity, etc.
    """
    from sqlalchemy import func
    
    # Count queries
    stats = {
        "total_stations": db.query(Station).count(),
        "total_users": db.query(AppUser).count(),
        "active_users": db.query(AppUser).filter(AppUser.is_active == True).count(),
        "total_alerts": db.query(Alert).count(),
        "active_alerts": db.query(Alert).filter(Alert.is_active == True).count(),
        "total_readings": db.query(AirQualityReading).count(),
        "total_reports": db.query(Report).count(),
    }
    
    # Recent activity
    last_24h = datetime.utcnow() - timedelta(hours=24)
    stats["recent_activity"] = {
        "readings_24h": db.query(AirQualityReading).filter(
            AirQualityReading.datetime >= last_24h
        ).count(),
        "alerts_triggered_24h": db.query(Alert).filter(
            Alert.triggered_at >= last_24h
        ).count(),
    }
    
    # Storage statistics
    stats["storage"] = {
        "database_size_estimate_mb": stats["total_readings"] * 0.001,  # Rough estimate
    }
    
    return stats


# =====================================================
# JOB MANAGEMENT
# =====================================================

@router.get("/jobs/status")
def get_jobs_status():
    """Get status of all scheduled jobs"""
    return scheduler.get_job_status()


@router.post("/jobs/run/{job_name}")
async def run_job_manually(job_name: str):
    """
    Manually trigger a job
    job_name: "ingestion" or "aggregation"
    """
    result = await scheduler.run_now(job_name)
    if result is None:
        raise HTTPException(status_code=400, detail=f"Unknown job: {job_name}")
    return {"message": f"Job {job_name} triggered", "result": result}


# =====================================================
# PROVIDER MANAGEMENT
# =====================================================

@router.get("/providers")
def get_providers(db: Session = Depends(get_db)):
    """Get all data providers"""
    providers = db.query(Provider).all()
    return providers


@router.post("/providers")
def create_provider(
    name: str,
    api_endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    ingestion_frequency_minutes: int = 30,
    db: Session = Depends(get_db)
):
    """Create a new data provider"""
    provider = Provider(
        name=name,
        api_endpoint=api_endpoint,
        api_key=api_key,
        ingestion_frequency_minutes=ingestion_frequency_minutes
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@router.delete("/providers/{provider_id}")
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    """Delete a provider"""
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    db.delete(provider)
    db.commit()
    return {"message": "Provider deleted"}


# =====================================================
# STATION MANAGEMENT
# =====================================================

@router.get("/stations", response_model=List[StationResponse])
def admin_get_stations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all stations (admin view with more details)"""
    stations = db.query(Station).offset(skip).limit(limit).all()
    return stations


@router.post("/stations", response_model=StationResponse)
def create_station(station: StationCreate, db: Session = Depends(get_db)):
    """Create a new monitoring station"""
    db_station = Station(**station.dict())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station


@router.put("/stations/{station_id}", response_model=StationResponse)
def update_station(
    station_id: int,
    station: StationCreate,
    db: Session = Depends(get_db)
):
    """Update station information"""
    db_station = db.query(Station).filter(Station.id == station_id).first()
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    for key, value in station.dict().items():
        setattr(db_station, key, value)
    
    db.commit()
    db.refresh(db_station)
    return db_station


@router.delete("/stations/{station_id}")
def delete_station(station_id: int, db: Session = Depends(get_db)):
    """Delete a station"""
    db_station = db.query(Station).filter(Station.id == station_id).first()
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    db.delete(db_station)
    db.commit()
    return {"message": "Station deleted"}


# =====================================================
# USER MANAGEMENT
# =====================================================

@router.get("/users", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all users with optional filters"""
    query = db.query(AppUser)
    
    if role_id:
        query = query.filter(AppUser.role_id == role_id)
    if is_active is not None:
        query = query.filter(AppUser.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get specific user details"""
    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user information"""
    db_user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Deactivate a user (soft delete)"""
    db_user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = False
    db.commit()
    return {"message": "User deactivated"}


# =====================================================
# ROLE & PERMISSION MANAGEMENT
# =====================================================

@router.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    """Get all roles"""
    roles = db.query(Role).all()
    return roles


@router.get("/permissions")
def get_permissions(db: Session = Depends(get_db)):
    """Get all permissions"""
    permissions = db.query(Permission).all()
    return permissions


# =====================================================
# AUDIT LOGS (from MongoDB)
# =====================================================

@router.get("/logs/api")
async def get_api_logs(
    limit: int = 100,
    skip: int = 0
):
    """Get API access logs from MongoDB"""
    from database.mongo_db import get_api_logs_collection
    
    collection = get_api_logs_collection()
    logs = await collection.find().sort("timestamp", -1).skip(skip).limit(limit).to_list(length=limit)
    
    # Convert ObjectId to string for JSON serialization
    for log in logs:
        log["_id"] = str(log["_id"])
    
    return logs


@router.get("/logs/errors")
async def get_error_logs(
    limit: int = 100,
    skip: int = 0,
    severity: Optional[str] = None
):
    """Get error logs from MongoDB"""
    from database.mongo_db import get_error_logs_collection
    
    collection = get_error_logs_collection()
    
    query = {}
    if severity:
        query["severity"] = severity
    
    logs = await collection.find(query).sort("timestamp", -1).skip(skip).limit(limit).to_list(length=limit)
    
    for log in logs:
        log["_id"] = str(log["_id"])
    
    return logs


@router.get("/logs/ingestion")
async def get_ingestion_logs(
    limit: int = 100,
    skip: int = 0,
    status: Optional[str] = None
):
    """Get data ingestion logs from MongoDB"""
    from database.mongo_db import get_data_ingestion_logs_collection
    
    collection = get_data_ingestion_logs_collection()
    
    query = {}
    if status:
        query["status"] = status
    
    logs = await collection.find(query).sort("timestamp", -1).skip(skip).limit(limit).to_list(length=limit)
    
    for log in logs:
        log["_id"] = str(log["_id"])
    
    return logs


# =====================================================
# DATA SEEDING
# =====================================================

@router.post("/seed/historical-data")
def seed_historical_data(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to generate"),
    db: Session = Depends(get_db)
):
    """
    Generate mock historical data for reports
    Creates readings every 2 hours for all stations and pollutants
    """
    from jobs.seed_historical_data import seed_historical_data
    
    try:
        seed_historical_data(days)
        
        # Count new readings
        total_readings = db.query(AirQualityReading).count()
        
        return {
            "status": "success",
            "message": f"Successfully generated {days} days of historical data",
            "total_readings": total_readings,
            "estimated_new_readings": days * 12 * 5 * 6  # days * readings_per_day * stations * pollutants
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to seed historical data: {str(e)}"
        )
