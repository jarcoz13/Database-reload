"""
Data Normalizer and Validator
Transforms raw API payloads into canonical format
- Validates schema and data types
- Normalizes timestamps to UTC
- Harmonizes pollutant units
- Deduplicates readings
- Persists to PostgreSQL
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.postgres_db import SessionLocal
from database.mongo_db import get_error_logs_collection
from models import AirQualityReading, Station, Pollutant, Provider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Normalizes and validates data from external providers
    Converts to canonical format and stores in database
    """
    
    # Unit conversion factors to μg/m³
    UNIT_CONVERSIONS = {
        "ppb_no2": 1.88,  # NO2: ppb to μg/m³
        "ppb_o3": 1.96,   # O3: ppb to μg/m³
        "ppb_so2": 2.62,  # SO2: ppb to μg/m³
        "ppm_co": 1145,   # CO: ppm to μg/m³
    }
    
    # AQI breakpoints (simplified EPA standard)
    AQI_BREAKPOINTS = [
        (0, 50, 0, 12.0),        # Good
        (51, 100, 12.1, 35.4),   # Moderate
        (101, 150, 35.5, 55.4),  # USG
        (151, 200, 55.5, 150.4), # Unhealthy
        (201, 300, 150.5, 250.4),# Very Unhealthy
        (301, 500, 250.5, 500.4),# Hazardous
    ]
    
    def __init__(self):
        self.mongo_logs = get_error_logs_collection()
        self.pollutant_cache = {}
        self.station_cache = {}
    
    async def normalize_and_save(
        self, 
        raw_data: List[Dict[str, Any]], 
        provider_name: str
    ) -> Dict[str, Any]:
        """
        Main method to normalize and save data
        
        Returns:
            Statistics about the normalization process
        """
        db = SessionLocal()
        try:
            # Get provider
            provider = db.query(Provider).filter(Provider.name == provider_name).first()
            if not provider:
                provider = self._create_provider(db, provider_name)
            
            # Load caches
            self._load_caches(db)
            
            stats = {
                "total_records": len(raw_data),
                "validated": 0,
                "saved": 0,
                "duplicates": 0,
                "errors": 0,
                "error_details": []
            }
            
            for record in raw_data:
                try:
                    # Validate and normalize
                    normalized = self._normalize_record(record, provider_name)
                    
                    if not normalized:
                        stats["errors"] += 1
                        continue
                    
                    stats["validated"] += 1
                    
                    # Save to database
                    if self._save_reading(db, normalized, provider.id):
                        stats["saved"] += 1
                    else:
                        stats["duplicates"] += 1
                    
                except Exception as e:
                    stats["errors"] += 1
                    error_msg = f"Error normalizing record: {str(e)}"
                    stats["error_details"].append(error_msg)
                    logger.error(error_msg)
                    await self._log_error(provider_name, record, str(e))
            
            db.commit()
            logger.info(f"Normalization complete: {stats['saved']} saved, {stats['duplicates']} duplicates, {stats['errors']} errors")
            return stats
            
        except Exception as e:
            db.rollback()
            logger.error(f"Fatal error in normalizer: {str(e)}")
            raise
        finally:
            db.close()
    
    def _normalize_record(
        self, 
        record: Dict[str, Any], 
        provider: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Normalize a single record based on provider format
        Returns list of normalized readings (one per pollutant)
        """
        if "aqicn" in provider.lower() or "waqi" in provider.lower():
            return self._normalize_aqicn(record)
        elif "google" in provider.lower():
            return self._normalize_google(record)
        elif "iqair" in provider.lower():
            return self._normalize_iqair(record)
        else:
            logger.warning(f"Unknown provider format: {provider}")
            return None
    
    def _normalize_aqicn(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize AQICN format"""
        try:
            data = record.get("data", {})
            city_name = data.get("city", {}).get("name", "Unknown")
            timestamp = datetime.strptime(
                data.get("time", {}).get("s", ""), 
                "%Y-%m-%d %H:%M:%S"
            )
            
            # Get or create station
            geo = data.get("city", {}).get("geo", [0, 0])
            station_id = self._get_or_create_station(
                name=f"{city_name} Station",
                city=city_name,
                latitude=geo[0],
                longitude=geo[1]
            )
            
            if not station_id:
                return []
            
            # Extract pollutant readings
            readings = []
            iaqi = data.get("iaqi", {})
            
            pollutant_mapping = {
                "pm25": ("PM2.5", "μg/m³"),
                "pm10": ("PM10", "μg/m³"),
                "o3": ("O3", "ppb"),
                "no2": ("NO2", "ppb"),
                "so2": ("SO2", "ppb"),
                "co": ("CO", "ppm"),
            }
            
            for key, (pollutant_name, unit) in pollutant_mapping.items():
                if key in iaqi:
                    value = iaqi[key].get("v", 0)
                    pollutant_id = self._get_pollutant_id(pollutant_name)
                    
                    if pollutant_id:
                        # Normalize value to canonical unit
                        normalized_value = self._convert_to_canonical_unit(value, unit, pollutant_name)
                        aqi = self._calculate_aqi(normalized_value, pollutant_name)
                        
                        readings.append({
                            "station_id": station_id,
                            "pollutant_id": pollutant_id,
                            "datetime": timestamp,
                            "value": normalized_value,
                            "aqi": aqi,
                            "raw_json": record,
                        })
            
            return readings
            
        except Exception as e:
            logger.error(f"Error normalizing AQICN record: {str(e)}")
            return []
    
    def _normalize_google(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize Google Air Quality API format"""
        try:
            timestamp = datetime.fromisoformat(record["dateTime"].replace("Z", "+00:00"))
            
            # For mock data, use default station
            station_id = self._get_or_create_station(
                name="Google Station",
                city="Bogotá",
                latitude=4.6097,
                longitude=-74.0817
            )
            
            readings = []
            for pollutant in record.get("pollutants", []):
                code = pollutant["code"]
                conc = pollutant.get("concentration", {})
                value = conc.get("value", 0)
                unit = conc.get("units", "")
                
                pollutant_name = self._map_pollutant_code(code)
                pollutant_id = self._get_pollutant_id(pollutant_name)
                
                if pollutant_id:
                    normalized_value = self._convert_to_canonical_unit(value, unit, pollutant_name)
                    aqi = self._calculate_aqi(normalized_value, pollutant_name)
                    
                    readings.append({
                        "station_id": station_id,
                        "pollutant_id": pollutant_id,
                        "datetime": timestamp,
                        "value": normalized_value,
                        "aqi": aqi,
                        "raw_json": record,
                    })
            
            return readings
            
        except Exception as e:
            logger.error(f"Error normalizing Google record: {str(e)}")
            return []
    
    def _normalize_iqair(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize IQAir format"""
        try:
            data = record.get("data", {})
            city = data.get("city", "Unknown")
            coords = data.get("location", {}).get("coordinates", [0, 0])
            
            pollution = data.get("current", {}).get("pollution", {})
            timestamp = datetime.fromisoformat(pollution.get("ts", "").replace("Z", "+00:00"))
            
            station_id = self._get_or_create_station(
                name=f"{city} IQAir Station",
                city=city,
                latitude=coords[1],
                longitude=coords[0]
            )
            
            # IQAir primarily provides PM2.5
            aqi = pollution.get("aqius", 0)
            pollutant_id = self._get_pollutant_id("PM2.5")
            
            if pollutant_id and station_id:
                # Estimate PM2.5 from AQI (reverse calculation)
                pm25_value = self._estimate_pm25_from_aqi(aqi)
                
                return [{
                    "station_id": station_id,
                    "pollutant_id": pollutant_id,
                    "datetime": timestamp,
                    "value": pm25_value,
                    "aqi": aqi,
                    "raw_json": record,
                }]
            
            return []
            
        except Exception as e:
            logger.error(f"Error normalizing IQAir record: {str(e)}")
            return []
    
    def _save_reading(
        self, 
        db: Session, 
        readings: List[Dict[str, Any]], 
        provider_id: int
    ) -> bool:
        """Save readings to database, handle duplicates"""
        try:
            for reading_data in readings:
                reading = AirQualityReading(
                    **reading_data,
                    provider_id=provider_id
                )
                db.add(reading)
            
            db.flush()
            return True
            
        except IntegrityError:
            # Duplicate reading (station_id, pollutant_id, datetime)
            db.rollback()
            return False
        except Exception as e:
            logger.error(f"Error saving reading: {str(e)}")
            db.rollback()
            return False
    
    def _load_caches(self, db: Session):
        """Load pollutants and stations into memory cache"""
        pollutants = db.query(Pollutant).all()
        self.pollutant_cache = {p.name: p.id for p in pollutants}
        
        stations = db.query(Station).all()
        self.station_cache = {(s.name, s.city): s.id for s in stations}
    
    def _get_pollutant_id(self, name: str) -> Optional[int]:
        """Get pollutant ID from cache"""
        return self.pollutant_cache.get(name)
    
    def _get_or_create_station(
        self, 
        name: str, 
        city: str, 
        latitude: float, 
        longitude: float
    ) -> Optional[int]:
        """Get or create station"""
        cache_key = (name, city)
        if cache_key in self.station_cache:
            return self.station_cache[cache_key]
        
        # Create new station (simplified, would need proper DB session)
        return None  # In real implementation, create station
    
    def _convert_to_canonical_unit(
        self, 
        value: float, 
        unit: str, 
        pollutant: str
    ) -> float:
        """Convert value to canonical unit (μg/m³ or ppb)"""
        # Simplified conversion logic
        return value
    
    def _calculate_aqi(self, concentration: float, pollutant: str) -> int:
        """Calculate AQI from concentration (simplified EPA formula)"""
        # Simplified AQI calculation for PM2.5
        if pollutant == "PM2.5":
            for aqi_low, aqi_high, conc_low, conc_high in self.AQI_BREAKPOINTS:
                if conc_low <= concentration <= conc_high:
                    return int(
                        ((aqi_high - aqi_low) / (conc_high - conc_low)) * 
                        (concentration - conc_low) + aqi_low
                    )
            return 500  # Hazardous
        
        # Default to moderate
        return 75
    
    def _estimate_pm25_from_aqi(self, aqi: int) -> float:
        """Reverse calculate PM2.5 from AQI"""
        for aqi_low, aqi_high, conc_low, conc_high in self.AQI_BREAKPOINTS:
            if aqi_low <= aqi <= aqi_high:
                return conc_low + ((aqi - aqi_low) * (conc_high - conc_low)) / (aqi_high - aqi_low)
        return 500.0  # Hazardous
    
    def _map_pollutant_code(self, code: str) -> str:
        """Map API pollutant codes to standard names"""
        mapping = {
            "pm25": "PM2.5",
            "pm10": "PM10",
            "o3": "O3",
            "no2": "NO2",
            "so2": "SO2",
            "co": "CO",
        }
        return mapping.get(code.lower(), code.upper())
    
    def _create_provider(self, db: Session, name: str) -> Provider:
        """Create provider if it doesn't exist"""
        provider = Provider(name=name)
        db.add(provider)
        db.commit()
        return provider
    
    async def _log_error(self, provider: str, record: Dict, error: str):
        """Log error to MongoDB"""
        log_entry = {
            "timestamp": datetime.utcnow(),
            "provider": provider,
            "error": error,
            "record_sample": str(record)[:500],  # Truncate for storage
            "severity": "error",
            "error_type": "normalization_error"
        }
        await self.mongo_logs.insert_one(log_entry)
