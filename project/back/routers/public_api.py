"""
Public REST API Router
Serves citizen and researcher requests for air quality data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database.postgres_db import get_db
from models import Station, AirQualityReading, Alert, Recommendation, AirQualityDailyStats, Pollutant
from schemas import (
    StationResponse, ReadingResponse, AlertResponse, AlertCreate, AlertUpdate,
    RecommendationResponse, DailyStatsResponse
)

router = APIRouter(prefix="/api", tags=["public"])


# =====================================================
# STATIONS
# =====================================================

@router.get("/stations", response_model=List[StationResponse])
def get_stations(
    city: Optional[str] = None,
    country: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of monitoring stations
    Optionally filter by city or country
    """
    query = db.query(Station)
    
    if city:
        query = query.filter(Station.city.ilike(f"%{city}%"))
    if country:
        query = query.filter(Station.country.ilike(f"%{country}%"))
    
    stations = query.offset(skip).limit(limit).all()
    return stations


@router.get("/stations/{station_id}", response_model=StationResponse)
def get_station(station_id: int, db: Session = Depends(get_db)):
    """Get details of a specific station"""
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


# =====================================================
# AIR QUALITY READINGS
# =====================================================

@router.get("/readings/current")
def get_current_readings(
    station_id: Optional[int] = None,
    city: Optional[str] = None,
    pollutant_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get most recent air quality readings
    Can filter by station, city, or pollutant
    """
    # Get readings from last 24 hours
    since = datetime.utcnow() - timedelta(hours=24)
    
    query = db.query(AirQualityReading).filter(
        AirQualityReading.datetime >= since
    )
    
    if station_id:
        query = query.filter(AirQualityReading.station_id == station_id)
    
    if pollutant_id:
        query = query.filter(AirQualityReading.pollutant_id == pollutant_id)
    
    if city:
        query = query.join(Station).filter(Station.city.ilike(f"%{city}%"))
    
    readings = query.order_by(AirQualityReading.datetime.desc()).limit(limit).all()
    
    return readings


@router.get("/readings/historical")
def get_historical_readings(
    station_id: int,
    pollutant_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """
    Get historical readings for a specific station and pollutant
    Date range required
    """
    if (end_date - start_date).days > 90:
        raise HTTPException(
            status_code=400, 
            detail="Date range too large. Maximum 90 days for raw readings. Use daily stats for longer periods."
        )
    
    readings = db.query(AirQualityReading).filter(
        AirQualityReading.station_id == station_id,
        AirQualityReading.pollutant_id == pollutant_id,
        AirQualityReading.datetime >= start_date,
        AirQualityReading.datetime <= end_date
    ).order_by(AirQualityReading.datetime.asc()).all()
    
    return readings


@router.get("/readings/latest/{station_id}")
def get_latest_by_station(
    station_id: int,
    db: Session = Depends(get_db)
):
    """
    Get latest reading for each pollutant at a specific station
    Useful for dashboard "current conditions" displays
    """
    # Subquery to get latest reading per pollutant
    from sqlalchemy import func
    
    latest_readings = []
    pollutants = db.query(Pollutant).all()
    
    for pollutant in pollutants:
        reading = db.query(AirQualityReading).filter(
            AirQualityReading.station_id == station_id,
            AirQualityReading.pollutant_id == pollutant.id
        ).order_by(AirQualityReading.datetime.desc()).first()
        
        if reading:
            latest_readings.append({
                "pollutant": pollutant.name,
                "value": reading.value,
                "aqi": reading.aqi,
                "datetime": reading.datetime,
                "unit": pollutant.unit
            })
    
    return latest_readings


# =====================================================
# DAILY STATISTICS
# =====================================================

@router.get("/stats/daily", response_model=List[DailyStatsResponse])
def get_daily_stats(
    station_id: int,
    pollutant_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 365,
    db: Session = Depends(get_db)
):
    """
    Get pre-aggregated daily statistics
    More efficient than querying raw readings for trends
    """
    from datetime import date
    
    query = db.query(AirQualityDailyStats).filter(
        AirQualityDailyStats.station_id == station_id
    )
    
    if pollutant_id:
        query = query.filter(AirQualityDailyStats.pollutant_id == pollutant_id)
    
    if start_date:
        query = query.filter(AirQualityDailyStats.date >= start_date)
    
    if end_date:
        query = query.filter(AirQualityDailyStats.date <= end_date)
    
    stats = query.order_by(AirQualityDailyStats.date.desc()).limit(limit).all()
    
    return stats


# =====================================================
# ALERTS (User-specific, requires authentication)
# =====================================================

@router.get("/alerts", response_model=List[AlertResponse])
def get_user_alerts(
    user_id: int = Query(..., description="User ID (from auth token)"),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get user's configured alerts
    TODO: Extract user_id from JWT token instead of query param
    """
    query = db.query(Alert).filter(Alert.user_id == user_id)
    
    if is_active is not None:
        query = query.filter(Alert.is_active == is_active)
    
    alerts = query.all()
    return alerts


@router.post("/alerts", response_model=AlertResponse)
def create_alert(
    alert: AlertCreate,
    user_id: int = Query(..., description="User ID (from auth token)"),
    db: Session = Depends(get_db)
):
    """Create a new alert for the user"""
    db_alert = Alert(**alert.dict(), user_id=user_id)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.patch("/alerts/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    user_id: int = Query(..., description="User ID (from auth token)"),
    db: Session = Depends(get_db)
):
    """Update an existing alert"""
    db_alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == user_id
    ).first()
    
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    for key, value in alert_update.dict(exclude_unset=True).items():
        setattr(db_alert, key, value)
    
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.delete("/alerts/{alert_id}")
def delete_alert(
    alert_id: int,
    user_id: int = Query(..., description="User ID (from auth token)"),
    db: Session = Depends(get_db)
):
    """Delete an alert"""
    db_alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == user_id
    ).first()
    
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(db_alert)
    db.commit()
    return {"message": "Alert deleted successfully"}


# =====================================================
# RECOMMENDATIONS
# =====================================================

@router.get("/recommendations", response_model=List[RecommendationResponse])
def get_recommendations(
    user_id: int = Query(..., description="User ID (from auth token)"),
    station_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get personalized health recommendations
    Based on recent air quality conditions
    """
    query = db.query(Recommendation).filter(Recommendation.user_id == user_id)
    
    if station_id:
        query = query.filter(Recommendation.station_id == station_id)
    
    recommendations = query.order_by(
        Recommendation.created_at.desc()
    ).limit(limit).all()
    
    return recommendations


# =====================================================
# POLLUTANTS
# =====================================================

@router.get("/pollutants")
def get_pollutants(db: Session = Depends(get_db)):
    """Get list of all monitored pollutants"""
    pollutants = db.query(Pollutant).all()
    return pollutants
