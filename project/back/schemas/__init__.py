"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date


# =====================================================
# User Schemas
# =====================================================

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    location: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role_id: int = 1  # Default to Citizen

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    role_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# Station Schemas
# =====================================================

class StationBase(BaseModel):
    name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    city: str
    country: str

class StationCreate(StationBase):
    region_id: Optional[int] = None
    provider_id: Optional[int] = None

class StationResponse(StationBase):
    id: int
    region_id: Optional[int]
    provider_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# Air Quality Reading Schemas
# =====================================================

class ReadingBase(BaseModel):
    station_id: int
    pollutant_id: int
    datetime: datetime
    value: float
    aqi: Optional[int] = None

class ReadingCreate(ReadingBase):
    provider_id: Optional[int] = None
    raw_json: Optional[dict] = None

class ReadingResponse(ReadingBase):
    id: int
    provider_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# Alert Schemas
# =====================================================

class AlertBase(BaseModel):
    station_id: int
    pollutant_id: int
    threshold: float
    trigger_condition: str = "exceeds"
    notification_method: str = "in-app"

class AlertCreate(AlertBase):
    is_active: Optional[bool] = True

class AlertUpdate(BaseModel):
    threshold: Optional[float] = None
    trigger_condition: Optional[str] = None
    notification_method: Optional[str] = None
    is_active: Optional[bool] = None

class AlertResponse(AlertBase):
    id: int
    user_id: int
    is_active: bool
    triggered_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# Recommendation Schemas
# =====================================================

class RecommendationResponse(BaseModel):
    id: int
    user_id: int
    station_id: int
    aqi_band: Optional[int]
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# Report Schemas
# =====================================================

class ReportCreate(BaseModel):
    title: str
    start_date: date
    end_date: date
    station_id: Optional[int] = None
    pollutant_id: Optional[int] = None
    file_format: str = "CSV"

class ReportResponse(BaseModel):
    id: int
    user_id: int
    station_id: Optional[int]
    pollutant_id: Optional[int]
    title: str
    start_date: date
    end_date: date
    file_format: str
    file_path: Optional[str]
    created_at: datetime
    generated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# =====================================================
# Daily Stats Schemas
# =====================================================

class DailyStatsResponse(BaseModel):
    id: int
    station_id: int
    pollutant_id: int
    date: date
    avg_value: Optional[float]
    avg_aqi: Optional[int]
    max_aqi: Optional[int]
    min_aqi: Optional[int]
    readings_count: Optional[int]
    
    class Config:
        from_attributes = True


# =====================================================
# Authentication Schemas
# =====================================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
