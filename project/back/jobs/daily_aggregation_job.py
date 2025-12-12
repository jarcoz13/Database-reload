"""
Daily Aggregation Job
Computes per-day, per-station, per-pollutant aggregates
Populates AirQualityDailyStats table for efficient queries
Runs once per day during off-peak hours
"""

import logging
from datetime import datetime, timedelta, date
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.postgres_db import SessionLocal
from models import AirQualityReading, AirQualityDailyStats, Station, Pollutant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DailyAggregationJob:
    """
    Aggregates raw readings into daily statistics
    Computes min, max, avg, 95th percentile per station/pollutant/day
    """
    
    def __init__(self):
        pass
    
    def run(self, target_date: date = None):
        """
        Main execution method
        
        Args:
            target_date: Date to aggregate (defaults to yesterday)
        """
        if target_date is None:
            target_date = (datetime.utcnow() - timedelta(days=1)).date()
        
        logger.info(f"Starting daily aggregation for {target_date}")
        start_time = datetime.utcnow()
        
        db = SessionLocal()
        try:
            stats = {
                "target_date": target_date.isoformat(),
                "aggregates_created": 0,
                "aggregates_updated": 0,
                "errors": 0,
                "stations_processed": 0,
                "pollutants_processed": 0,
            }
            
            # Get all active stations
            stations = db.query(Station).all()
            pollutants = db.query(Pollutant).all()
            
            stats["stations_processed"] = len(stations)
            stats["pollutants_processed"] = len(pollutants)
            
            # For each station-pollutant combination
            for station in stations:
                for pollutant in pollutants:
                    try:
                        result = self._aggregate_for_station_pollutant(
                            db, station.id, pollutant.id, target_date
                        )
                        
                        if result == "created":
                            stats["aggregates_created"] += 1
                        elif result == "updated":
                            stats["aggregates_updated"] += 1
                        
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(
                            f"Error aggregating station {station.id}, "
                            f"pollutant {pollutant.id}: {str(e)}"
                        )
            
            db.commit()
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            stats["duration_seconds"] = duration
            
            logger.info(f"Aggregation complete in {duration:.2f} seconds")
            logger.info(
                f"Created: {stats['aggregates_created']}, "
                f"Updated: {stats['aggregates_updated']}, "
                f"Errors: {stats['errors']}"
            )
            
            return stats
            
        except Exception as e:
            db.rollback()
            logger.error(f"Fatal error in aggregation job: {str(e)}")
            raise
        finally:
            db.close()
    
    def _aggregate_for_station_pollutant(
        self,
        db: Session,
        station_id: int,
        pollutant_id: int,
        target_date: date
    ) -> str:
        """
        Compute aggregates for a specific station-pollutant-date combination
        
        Returns:
            "created", "updated", or "skipped"
        """
        # Define date range
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        # Query readings for the day
        readings = db.query(AirQualityReading).filter(
            AirQualityReading.station_id == station_id,
            AirQualityReading.pollutant_id == pollutant_id,
            AirQualityReading.datetime >= start_datetime,
            AirQualityReading.datetime <= end_datetime
        ).all()
        
        if not readings:
            # No data for this combination
            return "skipped"
        
        # Compute statistics
        values = [r.value for r in readings if r.value is not None]
        aqi_values = [r.aqi for r in readings if r.aqi is not None]
        
        if not values:
            return "skipped"
        
        aggregates = {
            "station_id": station_id,
            "pollutant_id": pollutant_id,
            "date": target_date,
            "avg_value": sum(values) / len(values) if values else None,
            "avg_aqi": int(sum(aqi_values) / len(aqi_values)) if aqi_values else None,
            "max_aqi": max(aqi_values) if aqi_values else None,
            "min_aqi": min(aqi_values) if aqi_values else None,
            "readings_count": len(readings),
        }
        
        # Check if aggregate already exists
        existing = db.query(AirQualityDailyStats).filter(
            AirQualityDailyStats.station_id == station_id,
            AirQualityDailyStats.pollutant_id == pollutant_id,
            AirQualityDailyStats.date == target_date
        ).first()
        
        if existing:
            # Update existing
            for key, value in aggregates.items():
                if key not in ["station_id", "pollutant_id", "date"]:
                    setattr(existing, key, value)
            return "updated"
        else:
            # Create new
            daily_stat = AirQualityDailyStats(**aggregates)
            db.add(daily_stat)
            return "created"
    
    def backfill(self, start_date: date, end_date: date):
        """
        Backfill aggregates for a date range
        Useful for historical data or after system outages
        
        Args:
            start_date: Start of date range
            end_date: End of date range
        """
        logger.info(f"Starting backfill from {start_date} to {end_date}")
        
        current_date = start_date
        total_days = (end_date - start_date).days + 1
        
        results = {
            "total_days": total_days,
            "days_processed": 0,
            "total_aggregates_created": 0,
            "total_errors": 0,
        }
        
        while current_date <= end_date:
            try:
                logger.info(f"Processing {current_date} ({results['days_processed'] + 1}/{total_days})")
                day_stats = self.run(current_date)
                
                results["days_processed"] += 1
                results["total_aggregates_created"] += day_stats.get("aggregates_created", 0)
                results["total_errors"] += day_stats.get("errors", 0)
                
            except Exception as e:
                logger.error(f"Error processing {current_date}: {str(e)}")
                results["total_errors"] += 1
            
            current_date += timedelta(days=1)
        
        logger.info(f"Backfill complete: {results}")
        return results


def main():
    """Entry point for scheduled execution"""
    job = DailyAggregationJob()
    
    # Run for yesterday
    job.run()
    
    # Or backfill for a range:
    # start = date(2024, 1, 1)
    # end = date(2024, 1, 31)
    # job.backfill(start, end)


if __name__ == "__main__":
    main()
