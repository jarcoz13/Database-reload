"""
SQLAlchemy models for the Air Quality Platform
Based on the architecture defined in docs/Diagram_ER/
Components: Geospatial & Monitoring, Users & Access Control, 
            Alerts & Recommendations, Reporting & Analytics
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, Boolean, Text, 
    ForeignKey, UniqueConstraint, CheckConstraint, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.postgres_db import Base


# =====================================================
# Component 1: GEOSPATIAL & MONITORING
# =====================================================

class MapRegion(Base):
    __tablename__ = 'mapregion'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    geom = Column(String)  # PostGIS geometry - simplified as string for now
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    stations = relationship("Station", back_populates="region")


class Provider(Base):
    __tablename__ = 'provider'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    api_endpoint = Column(String(500))
    api_key = Column(String(500))  # Should be encrypted in production
    ingestion_frequency_minutes = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    stations = relationship("Station", back_populates="provider")
    readings = relationship("AirQualityReading", back_populates="provider")


class Station(Base):
    __tablename__ = 'station'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    city = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    region_id = Column(Integer, ForeignKey('mapregion.id', ondelete='SET NULL'))
    provider_id = Column(Integer, ForeignKey('provider.id', ondelete='SET NULL'))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    region = relationship("MapRegion", back_populates="stations")
    provider = relationship("Provider", back_populates="stations")
    readings = relationship("AirQualityReading", back_populates="station")
    alerts = relationship("Alert", back_populates="station")
    recommendations = relationship("Recommendation", back_populates="station")
    reports = relationship("Report", back_populates="station")
    daily_stats = relationship("AirQualityDailyStats", back_populates="station")


class Pollutant(Base):
    __tablename__ = 'pollutant'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    unit = Column(String(50))  # e.g., μg/m³ or ppb
    description = Column(Text)
    
    # Relationships
    readings = relationship("AirQualityReading", back_populates="pollutant")
    alerts = relationship("Alert", back_populates="pollutant")
    reports = relationship("Report", back_populates="pollutant")
    daily_stats = relationship("AirQualityDailyStats", back_populates="pollutant")


class AirQualityReading(Base):
    __tablename__ = 'airqualityreading'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('station.id', ondelete='CASCADE'), nullable=False)
    pollutant_id = Column(Integer, ForeignKey('pollutant.id', ondelete='CASCADE'), nullable=False)
    provider_id = Column(Integer, ForeignKey('provider.id', ondelete='SET NULL'))
    datetime = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)  # Normalized to canonical units
    aqi = Column(Integer)
    raw_json = Column(JSON)  # Raw payload for audit trail
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    station = relationship("Station", back_populates="readings")
    pollutant = relationship("Pollutant", back_populates="readings")
    provider = relationship("Provider", back_populates="readings")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('station_id', 'pollutant_id', 'datetime', name='uq_reading'),
    )


# =====================================================
# Component 2: USERS & ACCESS CONTROL
# =====================================================

class Role(Base):
    __tablename__ = 'role'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # Citizen, Researcher, Administrator
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    users = relationship("AppUser", back_populates="role")
    role_permissions = relationship("RolePermission", back_populates="role")


class AppUser(Base):
    __tablename__ = 'appuser'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    location = Column(String(255))
    role_id = Column(Integer, ForeignKey('role.id', ondelete='RESTRICT'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    role = relationship("Role", back_populates="users")
    alerts = relationship("Alert", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    reports = relationship("Report", back_populates="user")


class Permission(Base):
    __tablename__ = 'permission'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # view_current_aqi, download_data, etc.
    description = Column(Text)
    
    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission")


class RolePermission(Base):
    __tablename__ = 'rolepermission'
    
    role_id = Column(Integer, ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permission.id', ondelete='CASCADE'), primary_key=True)
    
    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")


# =====================================================
# Component 3: ALERTS & RECOMMENDATIONS
# =====================================================

class Alert(Base):
    __tablename__ = 'alert'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('appuser.id', ondelete='CASCADE'), nullable=False)
    station_id = Column(Integer, ForeignKey('station.id', ondelete='CASCADE'), nullable=False)
    pollutant_id = Column(Integer, ForeignKey('pollutant.id', ondelete='CASCADE'), nullable=False)
    threshold = Column(Float, nullable=False)  # AQI or concentration threshold
    trigger_condition = Column(String(50))  # 'exceeds', 'falls_below'
    notification_method = Column(String(50))  # 'email', 'in-app'
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("AppUser", back_populates="alerts")
    station = relationship("Station", back_populates="alerts")
    pollutant = relationship("Pollutant", back_populates="alerts")


class Recommendation(Base):
    __tablename__ = 'recommendation'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('appuser.id', ondelete='CASCADE'), nullable=False)
    station_id = Column(Integer, ForeignKey('station.id', ondelete='CASCADE'), nullable=False)
    aqi_band = Column(Integer)  # 0=Good, 1=Moderate, 2=USG, 3=Unhealthy, 4=VeryUnhealthy, 5=Hazardous
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("AppUser", back_populates="recommendations")
    station = relationship("Station", back_populates="recommendations")
    product_recommendations = relationship("ProductRecommendation", back_populates="recommendation")


class ProductRecommendation(Base):
    __tablename__ = 'productrecommendation'
    
    id = Column(Integer, primary_key=True)
    recommendation_id = Column(Integer, ForeignKey('recommendation.id', ondelete='CASCADE'), nullable=False)
    product_name = Column(String(255), nullable=False)
    product_category = Column(String(100))
    product_url = Column(String(500))
    
    # Relationships
    recommendation = relationship("Recommendation", back_populates="product_recommendations")


# =====================================================
# Component 4: REPORTING & ANALYTICS
# =====================================================

class Report(Base):
    __tablename__ = 'report'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('appuser.id', ondelete='CASCADE'), nullable=False)
    station_id = Column(Integer, ForeignKey('station.id', ondelete='SET NULL'))
    pollutant_id = Column(Integer, ForeignKey('pollutant.id', ondelete='SET NULL'))
    title = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    file_format = Column(String(20))  # 'CSV', 'PDF'
    file_path = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    generated_at = Column(DateTime)
    
    # Relationships
    user = relationship("AppUser", back_populates="reports")
    station = relationship("Station", back_populates="reports")
    pollutant = relationship("Pollutant", back_populates="reports")


class AirQualityDailyStats(Base):
    __tablename__ = 'airqualitydailystats'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('station.id', ondelete='CASCADE'), nullable=False)
    pollutant_id = Column(Integer, ForeignKey('pollutant.id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False)
    avg_value = Column(Float)
    avg_aqi = Column(Integer)
    max_aqi = Column(Integer)
    min_aqi = Column(Integer)
    readings_count = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    station = relationship("Station", back_populates="daily_stats")
    pollutant = relationship("Pollutant", back_populates="daily_stats")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('station_id', 'pollutant_id', 'date', name='uq_daily_stats'),
    )
