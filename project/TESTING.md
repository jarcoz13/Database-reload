# Testing Guide

## Quick Start Testing

After running `docker-compose up -d`, test the system:

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"healthy",...}`

### 2. System Info

```bash
curl http://localhost:8000/
```

### 3. Admin Health Check

```bash
curl http://localhost:8000/admin/health
```

Should show PostgreSQL, MongoDB, and scheduler status.

### 4. Get Pollutants

```bash
curl http://localhost:8000/api/pollutants
```

Should return 6 pollutants (PM2.5, PM10, O3, NO2, SO2, CO).

### 5. Get Roles

```bash
curl http://localhost:8000/admin/roles
```

Should return 3 roles (Citizen, Researcher, Administrator).

### 6. Manually Trigger Ingestion Job

```bash
curl -X POST http://localhost:8000/admin/jobs/run/ingestion
```

This will fetch mock data from external APIs and store it.

### 7. Check Stations

```bash
curl http://localhost:8000/api/stations
```

After ingestion, should show stations created from mock data.

### 8. Get Current Readings

```bash
curl "http://localhost:8000/api/readings/current?limit=10"
```

Should return recent air quality readings.

### 9. View API Documentation

Open in browser: http://localhost:8000/docs

Interactive Swagger UI with all endpoints.

### 10. Check Job Status

```bash
curl http://localhost:8000/admin/jobs/status
```

Shows next run times for scheduled jobs.

## Testing Mock Services

### Test AQICN Mock

```python
from services.mock_providers import AQICNMockService

service = AQICNMockService()
data = service.get_station_data("bogota")
print(data)
```

### Test Google Mock

```python
from services.mock_providers import GoogleAirQualityMockService

service = GoogleAirQualityMockService()
data = service.get_current_conditions(4.6097, -74.0817)
print(data)
```

### Test IQAir Mock

```python
from services.mock_providers import IQAirMockService

service = IQAirMockService()
data = service.get_city_data("bogota")
print(data)
```

## Testing Jobs Manually

### Run Ingestion Job

```bash
docker-compose exec backend python -c "
import asyncio
from jobs.ingestion_job import IngestionJob
job = IngestionJob()
asyncio.run(job.run())
"
```

### Run Normalizer

```bash
docker-compose exec backend python -c "
import asyncio
from jobs.normalizer import DataNormalizer
from services.mock_providers import AQICNMockService

normalizer = DataNormalizer()
mock = AQICNMockService()
data = mock.get_all_stations()
result = asyncio.run(normalizer.normalize_and_save(data, 'AQICN Mock'))
print(result)
"
```

### Run Daily Aggregation

```bash
docker-compose exec backend python -c "
from jobs.daily_aggregation_job import DailyAggregationJob
from datetime import date, timedelta

job = DailyAggregationJob()
yesterday = date.today() - timedelta(days=1)
result = job.run(yesterday)
print(result)
"
```

## Database Queries

### Connect to PostgreSQL

```bash
docker-compose exec postgres psql -U airquality_user -d airquality_db
```

### Useful Queries

```sql
-- Count readings
SELECT COUNT(*) FROM airqualityreading;

-- Latest readings by station
SELECT s.name, p.name, aqr.value, aqr.aqi, aqr.datetime
FROM airqualityreading aqr
JOIN station s ON aqr.station_id = s.id
JOIN pollutant p ON aqr.pollutant_id = p.id
ORDER BY aqr.datetime DESC
LIMIT 10;

-- Daily stats
SELECT * FROM airqualitydailystats ORDER BY date DESC LIMIT 10;

-- Users by role
SELECT r.name, COUNT(u.id) as user_count
FROM role r
LEFT JOIN appuser u ON r.id = u.role_id
GROUP BY r.name;
```

### Connect to MongoDB

```bash
docker-compose exec mongodb mongosh -u admin -p admin_pass
```

```javascript
use airquality_logs

// Count logs
db.data_ingestion_logs.countDocuments()

// Recent ingestion logs
db.data_ingestion_logs.find().sort({timestamp: -1}).limit(5)

// Error logs
db.error_logs.find().sort({timestamp: -1}).limit(5)
```

## Load Testing

### Using Apache Bench

```bash
# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Test stations endpoint
ab -n 1000 -c 10 http://localhost:8000/api/stations
```

### Using Python

```python
import requests
import time

def load_test(url, requests_count=100):
    times = []
    for i in range(requests_count):
        start = time.time()
        response = requests.get(url)
        end = time.time()
        times.append(end - start)
        print(f"Request {i+1}: {response.status_code} - {(end-start)*1000:.2f}ms")
    
    avg = sum(times) / len(times)
    print(f"\nAverage time: {avg*1000:.2f}ms")
    print(f"Min: {min(times)*1000:.2f}ms")
    print(f"Max: {max(times)*1000:.2f}ms")

load_test("http://localhost:8000/api/stations")
```

## Common Issues

### Port Already in Use

```bash
# Find process
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Database Not Initialized

```bash
docker-compose exec backend python init_db.py
```

### Restart Everything

```bash
docker-compose down -v
docker-compose up -d --build
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f mongodb
```
