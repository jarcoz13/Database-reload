// MongoDB initialization script
db = db.getSiblingDB('airquality_logs');

// Create collections
db.createCollection('api_logs');
db.createCollection('error_logs');
db.createCollection('data_ingestion_logs');
db.createCollection('alert_history');

// Create indexes for api_logs
db.api_logs.createIndex({ "timestamp": -1 });
db.api_logs.createIndex({ "endpoint": 1 });
db.api_logs.createIndex({ "user_id": 1 });
db.api_logs.createIndex({ "status_code": 1 });

// Create indexes for error_logs
db.error_logs.createIndex({ "timestamp": -1 });
db.error_logs.createIndex({ "error_type": 1 });
db.error_logs.createIndex({ "severity": 1 });

// Create indexes for data_ingestion_logs
db.data_ingestion_logs.createIndex({ "timestamp": -1 });
db.data_ingestion_logs.createIndex({ "provider_id": 1 });
db.data_ingestion_logs.createIndex({ "status": 1 });

// Create indexes for alert_history
db.alert_history.createIndex({ "timestamp": -1 });
db.alert_history.createIndex({ "user_id": 1 });
db.alert_history.createIndex({ "alert_id": 1 });

// Create user for application
db.createUser({
  user: 'airquality_app',
  pwd: 'airquality_app_pass',
  roles: [
    {
      role: 'readWrite',
      db: 'airquality_logs'
    }
  ]
});

print('MongoDB initialized successfully for Air Quality application');
