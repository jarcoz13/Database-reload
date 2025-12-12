from motor.motor_asyncio import AsyncIOMotorClient
import os

# MongoDB configuration
MONGODB_USER = os.getenv("MONGODB_USER", "admin")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "admin_pass")
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = os.getenv("MONGODB_PORT", "27017")
MONGODB_DB = os.getenv("MONGODB_DB", "airquality_logs")

MONGODB_URL = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}"

# Create MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
database = client[MONGODB_DB]

# Dependency to get MongoDB database
async def get_mongo_db():
    return database

# Collections
def get_api_logs_collection():
    return database.api_logs

def get_error_logs_collection():
    return database.error_logs

def get_data_ingestion_logs_collection():
    return database.data_ingestion_logs

def get_alert_history_collection():
    return database.alert_history
