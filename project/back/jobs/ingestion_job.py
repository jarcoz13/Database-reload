"""
Data Ingestion Job
Polls external air quality APIs on a configurable schedule (10-60 minutes)
Fetches raw JSON payloads and passes them to the normalizer
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session

from database.postgres_db import SessionLocal
from database.mongo_db import get_data_ingestion_logs_collection
from services.mock_providers import MockServiceManager
from models import Provider
from jobs.normalizer import DataNormalizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IngestionJob:
    """
    Ingestion job that fetches data from external providers
    Runs on a schedule (every 10-60 minutes)
    """
    
    def __init__(self):
        self.mock_service = MockServiceManager()
        self.mongo_logs = get_data_ingestion_logs_collection()
        self.normalizer = DataNormalizer()
        
    async def run(self):
        """Main execution method"""
        logger.info("Starting ingestion job...")
        start_time = datetime.utcnow()
        
        db = SessionLocal()
        try:
            # Get active providers from database
            providers = db.query(Provider).all()
            
            if not providers:
                logger.warning("No providers configured. Using default mock providers.")
                providers = self._get_default_providers()
            
            results = {
                "job_start": start_time.isoformat(),
                "providers_processed": 0,
                "total_readings": 0,
                "errors": [],
            }
            
            # Fetch data from each provider
            for provider in providers:
                try:
                    logger.info(f"Fetching data from provider: {provider.name}")
                    provider_data = await self._fetch_provider_data(provider)
                    
                    if provider_data:
                        raw_count = len(provider_data)
                        
                        # Normalize and save to database
                        norm_stats = await self.normalizer.normalize_and_save(provider_data, provider.name)
                        results["total_readings"] += norm_stats.get("saved", 0)
                        
                        # Log to MongoDB
                        await self._log_ingestion(provider.name, provider_data, "success")
                        
                        logger.info(f"Fetched {raw_count} records from {provider.name}, saved {norm_stats.get('saved', 0)} readings")
                    
                except Exception as e:
                    error_msg = f"Error fetching data from {provider.name}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    await self._log_ingestion(provider.name, [], "error", str(e))
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            results["job_end"] = end_time.isoformat()
            results["duration_seconds"] = duration
            
            logger.info(f"Ingestion job completed in {duration:.2f} seconds")
            logger.info(f"Processed {results['providers_processed']} providers, {results['total_readings']} readings")
            
            return results
            
        except Exception as e:
            logger.error(f"Fatal error in ingestion job: {str(e)}")
            raise
        finally:
            db.close()
    
    async def _fetch_provider_data(self, provider: Provider) -> List[Dict[str, Any]]:
        """
        Fetch data from a specific provider
        In production, this would make actual API calls
        For now, uses mock services
        """
        provider_name = provider.name.lower()
        
        if "aqicn" in provider_name or "waqi" in provider_name:
            data = self.mock_service.aqicn.get_all_stations()
        elif "google" in provider_name:
            data = [
                self.mock_service.google.get_current_conditions(4.6097, -74.0817),
                self.mock_service.google.get_current_conditions(6.2442, -75.5812),
            ]
        elif "iqair" in provider_name or "airvisual" in provider_name:
            data = [
                self.mock_service.iqair.get_city_data("bogota"),
                self.mock_service.iqair.get_city_data("medellin"),
            ]
        else:
            logger.warning(f"Unknown provider type: {provider.name}, using AQICN mock")
            data = self.mock_service.aqicn.get_all_stations()
        
        return data
    
    async def _log_ingestion(
        self, 
        provider: str, 
        data: List[Dict], 
        status: str, 
        error: str = None
    ):
        """Log ingestion activity to MongoDB"""
        log_entry = {
            "timestamp": datetime.utcnow(),
            "provider": provider,
            "status": status,
            "records_fetched": len(data),
            "error": error,
        }
        
        await self.mongo_logs.insert_one(log_entry)
    
    def _get_default_providers(self) -> List[Provider]:
        """Return mock provider objects for testing"""
        return [
            type('Provider', (), {'name': 'AQICN Mock', 'id': 1})(),
            type('Provider', (), {'name': 'Google Air Quality Mock', 'id': 2})(),
            type('Provider', (), {'name': 'IQAir Mock', 'id': 3})(),
        ]


async def main():
    """Entry point for scheduled execution"""
    job = IngestionJob()
    await job.run()


if __name__ == "__main__":
    asyncio.run(main())
