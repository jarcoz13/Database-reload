"""
Historical Data Seeder
Generates mock historical data to populate reports
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict
import logging

from sqlalchemy.orm import Session
from database.postgres_db import SessionLocal
from models import AirQualityReading, Station, Pollutant, Provider

logger = logging.getLogger(__name__)


class HistoricalDataSeeder:
    """Seeds database with historical mock data for reports"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def generate_historical_data(self, days_back: int = 30):
        """
        Generate historical data for the last N days
        
        Args:
            days_back: Number of days to generate data for
        """
        try:
            logger.info(f"Starting historical data generation for {days_back} days")
            
            # Get all active stations
            stations = self.db.query(Station).all()
            if not stations:
                logger.error("No stations found in database")
                return
            
            # Get all pollutants
            pollutants = self.db.query(Pollutant).all()
            if not pollutants:
                logger.error("No pollutants found in database")
                return
            
            # Get mock provider (ID 6 is IQAir Mock)
            provider = self.db.query(Provider).filter(Provider.id == 6).first()
            if not provider:
                logger.error("Mock provider not found")
                return
            
            # Generate data for each day
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            total_readings = 0
            current_date = start_date
            
            while current_date <= end_date:
                # Generate multiple readings per day (every 2 hours = 12 readings/day)
                for hour in range(0, 24, 2):
                    reading_time = current_date.replace(hour=hour, minute=0, second=0)
                    
                    # Skip future times
                    if reading_time > end_date:
                        break
                    
                    # Generate readings for each station and pollutant
                    for station in stations:
                        for pollutant in pollutants:
                            reading = self._generate_mock_reading(
                                station=station,
                                pollutant=pollutant,
                                provider=provider,
                                timestamp=reading_time
                            )
                            
                            # Check for duplicates
                            existing = self.db.query(AirQualityReading).filter(
                                AirQualityReading.station_id == reading.station_id,
                                AirQualityReading.pollutant_id == reading.pollutant_id,
                                AirQualityReading.datetime == reading.datetime
                            ).first()
                            
                            if not existing:
                                self.db.add(reading)
                                total_readings += 1
                    
                    # Commit in batches
                    if total_readings % 100 == 0:
                        self.db.commit()
                        logger.info(f"Saved {total_readings} readings so far...")
                
                current_date += timedelta(days=1)
            
            # Final commit
            self.db.commit()
            logger.info(f"Historical data generation complete: {total_readings} readings created")
            
        except Exception as e:
            logger.error(f"Error generating historical data: {str(e)}")
            self.db.rollback()
        finally:
            self.db.close()
    
    def _generate_mock_reading(
        self,
        station: Station,
        pollutant: Pollutant,
        provider: Provider,
        timestamp: datetime
    ) -> AirQualityReading:
        """Generate a single mock reading with realistic variations"""
        
        # Base values for different pollutants (realistic ranges)
        pollutant_ranges = {
            'PM2.5': (5, 150),    # μg/m³
            'PM10': (10, 200),    # μg/m³
            'O3': (10, 120),      # ppb
            'NO2': (5, 80),       # ppb
            'SO2': (0, 50),       # ppb
            'CO': (0.1, 5.0),     # ppm
        }
        
        # Get range for this pollutant (default if not found)
        min_val, max_val = pollutant_ranges.get(pollutant.name, (10, 100))
        
        # Add some daily variation (higher during day, lower at night)
        hour = timestamp.hour
        time_factor = 1.0
        if 6 <= hour <= 18:  # Daytime
            time_factor = 1.2
        elif 0 <= hour <= 5 or 22 <= hour <= 23:  # Night
            time_factor = 0.7
        
        # Add some weekly variation (higher on weekdays)
        weekday = timestamp.weekday()
        week_factor = 1.1 if weekday < 5 else 0.9  # Weekday vs weekend
        
        # Generate value with randomness
        base_value = random.uniform(min_val, max_val)
        value = base_value * time_factor * week_factor
        
        # Calculate AQI (simplified)
        aqi = self._calculate_aqi(pollutant.name, value)
        
        # Create reading
        reading = AirQualityReading(
            station_id=station.id,
            pollutant_id=pollutant.id,
            provider_id=provider.id,
            datetime=timestamp,
            value=round(value, 2),
            aqi=aqi,
            raw_json={
                "source": "mock_historical",
                "station": station.name,
                "pollutant": pollutant.name,
                "timestamp": timestamp.isoformat()
            }
        )
        
        return reading
    
    def _calculate_aqi(self, pollutant_name: str, value: float) -> int:
        """Calculate AQI based on pollutant concentration"""
        
        # Simplified AQI calculation
        aqi_breakpoints = {
            'PM2.5': [
                (0, 12, 0, 50),
                (12.1, 35.4, 51, 100),
                (35.5, 55.4, 101, 150),
                (55.5, 150.4, 151, 200),
                (150.5, 250.4, 201, 300),
                (250.5, 500, 301, 500)
            ],
            'PM10': [
                (0, 54, 0, 50),
                (55, 154, 51, 100),
                (155, 254, 101, 150),
                (255, 354, 151, 200),
                (355, 424, 201, 300),
                (425, 604, 301, 500)
            ],
            'O3': [
                (0, 54, 0, 50),
                (55, 70, 51, 100),
                (71, 85, 101, 150),
                (86, 105, 151, 200),
                (106, 200, 201, 300)
            ],
            'NO2': [
                (0, 53, 0, 50),
                (54, 100, 51, 100),
                (101, 360, 101, 150),
                (361, 649, 151, 200),
                (650, 1249, 201, 300)
            ],
            'SO2': [
                (0, 35, 0, 50),
                (36, 75, 51, 100),
                (76, 185, 101, 150),
                (186, 304, 151, 200),
                (305, 604, 201, 300)
            ],
            'CO': [
                (0, 4.4, 0, 50),
                (4.5, 9.4, 51, 100),
                (9.5, 12.4, 101, 150),
                (12.5, 15.4, 151, 200),
                (15.5, 30.4, 201, 300)
            ]
        }
        
        breakpoints = aqi_breakpoints.get(pollutant_name, [(0, 100, 0, 100)])
        
        for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
            if bp_lo <= value <= bp_hi:
                aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (value - bp_lo) + aqi_lo
                return int(aqi)
        
        # If value exceeds all breakpoints, return max
        return 500


def seed_historical_data(days_back: int = 30):
    """Entry point for seeding historical data"""
    seeder = HistoricalDataSeeder()
    seeder.generate_historical_data(days_back)


if __name__ == "__main__":
    import sys
    
    # Allow specifying days from command line
    days = 30
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print(f"Invalid days argument: {sys.argv[1]}, using default 30")
    
    print(f"Seeding {days} days of historical data...")
    seed_historical_data(days)
    print("Done!")
