# Air Quality Platform - Architecture Overview

## System Architecture

This project implements the architecture described in `src/Report_Latex/chapters/03_architecture.tex`.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│               CLIENTS & WEB FRONTEND                     │
│          (Vue.js - Citizens, Researchers, Admins)        │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────┐
│                    API LAYER                             │
│  ┌──────────────────┐    ┌──────────────────────────┐  │
│  │   Public API     │    │      Admin API           │  │
│  │ /api/*           │    │  /admin/*                │  │
│  │ (Citizens,       │    │ (System Management,      │  │
│  │  Researchers)    │    │  User Management, Logs)  │  │
│  └──────────────────┘    └──────────────────────────┘  │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────┐
│              DATA PERSISTENCE LAYER                      │
│  ┌─────────────────────┐    ┌──────────────────────┐   │
│  │   PostgreSQL         │    │     MongoDB          │   │
│  │ (Operational &       │    │ (Logs, Preferences,  │   │
│  │  Analytical Data)    │    │  Audit Trails)       │   │
│  └─────────────────────┘    └──────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────┐
│              BATCH PROCESSING LAYER                      │
│  ┌──────────────────┐  ┌────────────────────────────┐  │
│  │ Ingestion Job    │  │ Normalizer & Validator     │  │
│  │ (Every 30 min)   │→ │ (Data transformation)      │  │
│  └──────────────────┘  └────────────────────────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Daily Aggregation Job (02:00 UTC)               │   │
│  │ (Computes AirQualityDailyStats)                 │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### Data Model - Four Components

#### 1. Geospatial & Monitoring
- **Station**: Monitoring stations with geographic data
- **Pollutant**: Types of pollutants (PM2.5, PM10, O3, NO2, SO2, CO)
- **Provider**: External data sources (AQICN, Google, IQAir - Mocked)
- **AirQualityReading**: Raw sensor measurements (main fact table)
- **MapRegion**: Geographic regions for spatial analysis

#### 2. Users & Access Control
- **AppUser**: User accounts with authentication
- **Role**: User roles (Citizen, Researcher, Administrator)
- **Permission**: Granular permissions (RBAC)
- **RolePermission**: Many-to-many mapping

#### 3. Alerts & Recommendations
- **Alert**: User-configured air quality alerts
- **Recommendation**: Personalized health guidance
- **ProductRecommendation**: Product suggestions (masks, filters)

#### 4. Reporting & Analytics
- **Report**: Report metadata and exports
- **AirQualityDailyStats**: Pre-aggregated daily statistics (performance optimization)

### Technology Stack

- **Frontend**: Vue.js 3 + Vite + TypeScript
- **Backend**: FastAPI (Python 3.11+)
- **Primary Database**: PostgreSQL 15 with PostGIS
- **NoSQL Store**: MongoDB 7.0
- **Job Scheduling**: APScheduler
- **Containerization**: Docker + Docker Compose

### Key Features

#### Public API (`/api/*`)
- Station listing and details
- Current and historical air quality readings
- Daily aggregated statistics
- User alerts (CRUD operations)
- Personalized recommendations
- Pollutant information

#### Admin API (`/admin/*`)
- System health monitoring
- Database statistics
- Job management (manual triggering, status)
- Provider management
- Station CRUD operations
- User management
- Role and permission management
- Audit logs (MongoDB)

#### Batch Jobs
1. **Ingestion Job** (Every 30 minutes)
   - Polls mock external APIs (AQICN, Google, IQAir)
   - Fetches raw JSON payloads
   - Passes to normalizer

2. **Normalizer & Validator**
   - Schema validation
   - Timestamp normalization to UTC
   - Unit harmonization (to μg/m³)
   - Deduplication
   - AQI calculation
   - Persistence to PostgreSQL

3. **Daily Aggregation Job** (02:00 UTC)
   - Computes daily statistics per station/pollutant
   - Populates `AirQualityDailyStats` table
   - Improves dashboard query performance

### Mock Services

External API providers are mocked for development:

- **AQICNMockService**: Simulates AQICN (waqi.info) API
- **GoogleAirQualityMockService**: Simulates Google Air Quality API
- **IQAirMockService**: Simulates IQAir (AirVisual) API

Mock data includes realistic:
- Station coordinates (Colombian cities)
- Pollutant concentrations
- AQI values
- Health recommendations
- Timestamps

### Performance Optimizations

1. **Temporal Partitioning**: Monthly partitioning of `AirQualityReading`
2. **Materialized Views**: `AirQualityDailyStats` for aggregated queries
3. **Indexes**: Strategic B-tree and BRIN indexes on timestamp columns
4. **Query Caching**: API-level caching for frequent queries
5. **NoSQL Separation**: User preferences in MongoDB to avoid JSONB in PostgreSQL

### Data Flow

```
External APIs (Mock)
    ↓
Ingestion Job (Scheduled)
    ↓
Normalizer & Validator
    ↓
PostgreSQL (AirQualityReading)
    ↓
Daily Aggregation Job
    ↓
AirQualityDailyStats
    ↓
Public/Admin APIs
    ↓
Web Frontend
```

### Observability

- **MongoDB Collections** for logs:
  - `api_logs`: API request/response logs
  - `error_logs`: Application errors
  - `data_ingestion_logs`: Ingestion job activity
  - `alert_history`: Alert triggering history

### Directory Structure

```
project/back/
├── database/          # Database connections
├── models/            # SQLAlchemy models (14 entities)
├── schemas/           # Pydantic validation schemas
├── routers/           # API endpoints
│   ├── public_api.py  # Public REST API
│   └── admin_api.py   # Admin REST API
├── jobs/              # Batch processing
│   ├── ingestion_job.py
│   ├── normalizer.py
│   ├── daily_aggregation_job.py
│   └── scheduler.py
├── services/          # Business logic
│   └── mock_providers.py
└── main.py            # FastAPI application
```

### Compliance with Architecture Document

This implementation follows the specifications in:
- `src/Report_Latex/chapters/03_architecture.tex`
- `docs/Diagram_ER/Diagram_ER.dbml`
- `docs/Diagram_ER/init_database.sql`

All four data components are implemented with full relationships, constraints, and indexes as specified.
