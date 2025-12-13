"""
Job Scheduler
Manages execution of batch jobs on a schedule
Uses APScheduler for cron-like scheduling
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from jobs.ingestion_job import IngestionJob
from jobs.daily_aggregation_job import DailyAggregationJob
from jobs.alert_checker_job import AlertCheckerJob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobScheduler:
    """
    Manages scheduled execution of batch jobs
    According to architecture:
    - Ingestion: every 10-60 minutes (configurable)
    - Daily Aggregation: once per day at 02:00 UTC
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.ingestion_job = IngestionJob()
        self.aggregation_job = DailyAggregationJob()
        self.alert_checker_job = AlertCheckerJob()
        
    def start(self):
        """Start the scheduler with configured jobs"""
        logger.info("Initializing job scheduler...")
        
        # Ingestion Job: runs every 1 minute (for testing)
        self.scheduler.add_job(
            self.ingestion_job.run,
            trigger=CronTrigger(minute="*/1"),  # Every 1 minute
            id="ingestion_job",
            name="Data Ingestion Job",
            replace_existing=True,
            max_instances=1,
        )
        logger.info("Scheduled: Ingestion Job (every 1 minute)")
        
        # Daily Aggregation Job: runs at 02:00 UTC
        self.scheduler.add_job(
            self.aggregation_job.run,
            trigger=CronTrigger(hour=2, minute=0),  # 02:00 UTC
            id="daily_aggregation_job",
            name="Daily Aggregation Job",
            replace_existing=True,
            max_instances=1,
        )
        logger.info("Scheduled: Daily Aggregation Job (daily at 02:00 UTC)")
        # Alert Checker Job: runs every minute to check active alerts
        self.scheduler.add_job(
            self.alert_checker_job.run,
            trigger=CronTrigger(minute="*/1"),  # Every 1 minute
            id="alert_checker_job",
            name="Alert Checker Job",
            replace_existing=True,
            max_instances=1,
        )
        logger.info("Scheduled: Alert Checker Job (every 1 minute)")
        
        # 
        # Start scheduler
        self.scheduler.start()
        logger.info("Job scheduler started successfully")
        
        # Log next run times
        self._log_next_runs()
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping job scheduler...")
        self.scheduler.shutdown()
        logger.info("Job scheduler stopped")
    
    async def run_now(self, job_name: str):
        """Manually trigger a job"""
        if job_name == "ingestion_job":
            logger.info("Manually triggering ingestion job...")
            return await self.ingestion_job.run()
        elif job_name == "daily_aggregation_job":
            logger.info("Manually triggering aggregation job...")
            return await self.aggregation_job.run()
        elif job_name == "alert_checker_job":
            logger.info("Manually triggering alert checker job...")
            return await self.alert_checker_job.run()
        else:
            logger.error(f"Unknown job: {job_name}")
            return None
    
    def get_job_status(self):
        """Get status of all scheduled jobs"""
        jobs = self.scheduler.get_jobs()
        status = []
        
        for job in jobs:
            status.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        
        return status
    
    def _log_next_runs(self):
        """Log next run times for all jobs"""
        jobs = self.scheduler.get_jobs()
        for job in jobs:
            next_run = job.next_run_time
            if next_run:
                logger.info(f"Next run for {job.name}: {next_run.isoformat()}")


# Global scheduler instance
scheduler = JobScheduler()


async def start_scheduler():
    """Start the scheduler (called from main app)"""
    scheduler.start()


async def stop_scheduler():
    """Stop the scheduler (called on app shutdown)"""
    scheduler.stop()
