-- =====================================================
-- Air Quality Database - PostgreSQL Schema
-- With Indexing and PostGIS Support
-- =====================================================

-- Enable PostGIS extension for geospatial data
CREATE EXTENSION IF NOT EXISTS postgis;

-- =====================================================
-- GEOSPATIAL & MONITORING (Operational)
-- =====================================================

-- MapRegion Table
CREATE TABLE MapRegion (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    geom GEOMETRY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Provider Table
CREATE TABLE Provider (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    api_endpoint VARCHAR(500),
    api_key VARCHAR(500), -- Should be encrypted in production
    ingestion_frequency_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Station Table
CREATE TABLE Station (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    city VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    region_id INTEGER REFERENCES MapRegion(id) ON DELETE SET NULL,
    provider_id INTEGER REFERENCES Provider(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pollutant Table
CREATE TABLE Pollutant (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    unit VARCHAR(50), -- e.g., μg/m³ or ppb
    description TEXT
);

-- AirQualityReading Table
CREATE TABLE AirQualityReading (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES Station(id) ON DELETE CASCADE,
    pollutant_id INTEGER NOT NULL REFERENCES Pollutant(id) ON DELETE CASCADE,
    provider_id INTEGER REFERENCES Provider(id) ON DELETE SET NULL,
    datetime TIMESTAMP NOT NULL,
    value FLOAT NOT NULL, -- Normalized to canonical units
    aqi INTEGER,
    raw_json JSONB, -- Raw payload for audit trail
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- USERS & ACCESS CONTROL (Operational)
-- =====================================================

-- Role Table
CREATE TABLE Role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL, -- e.g., Citizen, Researcher, Administrator
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AppUser Table
CREATE TABLE AppUser (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    location VARCHAR(255),
    role_id INTEGER NOT NULL REFERENCES Role(id) ON DELETE RESTRICT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permission Table
CREATE TABLE Permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL, -- e.g., view_current_aqi, download_data
    description TEXT
);

-- RolePermission Junction Table
CREATE TABLE RolePermission (
    role_id INTEGER NOT NULL REFERENCES Role(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES Permission(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- =====================================================
-- ALERTS & RECOMMENDATIONS (Operational)
-- =====================================================

-- Alert Table
CREATE TABLE Alert (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES AppUser(id) ON DELETE CASCADE,
    station_id INTEGER NOT NULL REFERENCES Station(id) ON DELETE CASCADE,
    pollutant_id INTEGER NOT NULL REFERENCES Pollutant(id) ON DELETE CASCADE,
    threshold FLOAT NOT NULL, -- AQI or concentration threshold
    trigger_condition VARCHAR(50), -- e.g., 'exceeds', 'falls_below'
    notification_method VARCHAR(50), -- e.g., 'email', 'in-app'
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendation Table
CREATE TABLE Recommendation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES AppUser(id) ON DELETE CASCADE,
    station_id INTEGER NOT NULL REFERENCES Station(id) ON DELETE CASCADE,
    aqi_band INTEGER, -- EPA AQI band: 0=Good, 1=Moderate, etc.
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ProductRecommendation Table
CREATE TABLE ProductRecommendation (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER NOT NULL REFERENCES Recommendation(id) ON DELETE CASCADE,
    product_name VARCHAR(255) NOT NULL,
    product_category VARCHAR(100),
    product_url VARCHAR(500)
);

-- =====================================================
-- REPORTING & ANALYTICS (Operational and Analytical)
-- =====================================================

-- Report Table
CREATE TABLE Report (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES AppUser(id) ON DELETE CASCADE,
    station_id INTEGER REFERENCES Station(id) ON DELETE SET NULL,
    pollutant_id INTEGER REFERENCES Pollutant(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    file_format VARCHAR(20), -- e.g., 'CSV', 'PDF'
    file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_at TIMESTAMP
);

-- AirQualityDailyStats Table
CREATE TABLE AirQualityDailyStats (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES Station(id) ON DELETE CASCADE,
    pollutant_id INTEGER NOT NULL REFERENCES Pollutant(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    avg_value FLOAT,
    avg_aqi INTEGER,
    max_aqi INTEGER,
    min_aqi INTEGER,
    readings_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (station_id, pollutant_id, date)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- =====================================================

-- Geospatial indexes
CREATE INDEX idx_station_location ON Station USING gist(ST_MakePoint(longitude, latitude));
CREATE INDEX idx_mapregion_geom ON MapRegion USING gist(geom);

-- Station indexes
CREATE INDEX idx_station_city ON Station(city);
CREATE INDEX idx_station_country ON Station(country);
CREATE INDEX idx_station_region_id ON Station(region_id);
CREATE INDEX idx_station_provider_id ON Station(provider_id);

-- AirQualityReading indexes (critical for query performance)
CREATE INDEX idx_aqr_station_id ON AirQualityReading(station_id);
CREATE INDEX idx_aqr_pollutant_id ON AirQualityReading(pollutant_id);
CREATE INDEX idx_aqr_datetime ON AirQualityReading(datetime DESC);
CREATE INDEX idx_aqr_station_datetime ON AirQualityReading(station_id, datetime DESC);
CREATE INDEX idx_aqr_station_pollutant_datetime ON AirQualityReading(station_id, pollutant_id, datetime DESC);
CREATE INDEX idx_aqr_aqi ON AirQualityReading(aqi) WHERE aqi IS NOT NULL;
CREATE INDEX idx_aqr_raw_json ON AirQualityReading USING gin(raw_json);

-- User indexes
CREATE INDEX idx_appuser_email ON AppUser(email);
CREATE INDEX idx_appuser_username ON AppUser(username);
CREATE INDEX idx_appuser_role_id ON AppUser(role_id);
CREATE INDEX idx_appuser_is_active ON AppUser(is_active) WHERE is_active = TRUE;

-- Alert indexes
CREATE INDEX idx_alert_user_id ON Alert(user_id);
CREATE INDEX idx_alert_station_id ON Alert(station_id);
CREATE INDEX idx_alert_is_active ON Alert(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_alert_triggered_at ON Alert(triggered_at DESC);

-- Recommendation indexes
CREATE INDEX idx_recommendation_user_id ON Recommendation(user_id);
CREATE INDEX idx_recommendation_station_id ON Recommendation(station_id);
CREATE INDEX idx_recommendation_created_at ON Recommendation(created_at DESC);

-- Report indexes
CREATE INDEX idx_report_user_id ON Report(user_id);
CREATE INDEX idx_report_created_at ON Report(created_at DESC);
CREATE INDEX idx_report_date_range ON Report(start_date, end_date);

-- AirQualityDailyStats indexes
CREATE INDEX idx_aqdailystats_station_id ON AirQualityDailyStats(station_id);
CREATE INDEX idx_aqdailystats_pollutant_id ON AirQualityDailyStats(pollutant_id);
CREATE INDEX idx_aqdailystats_date ON AirQualityDailyStats(date DESC);
CREATE INDEX idx_aqdailystats_station_date ON AirQualityDailyStats(station_id, date DESC);

-- =====================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_appuser_updated_at BEFORE UPDATE ON AppUser
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- INITIAL DATA (Optional)
-- =====================================================

-- Insert default roles
INSERT INTO Role (name, description) VALUES
    ('Citizen', 'General public user with basic access'),
    ('Researcher', 'Academic or scientific researcher with extended access'),
    ('Administrator', 'System administrator with full access');

-- Insert default permissions
INSERT INTO Permission (name, description) VALUES
    ('view_current_aqi', 'View current air quality index'),
    ('view_historical_data', 'View historical air quality data'),
    ('download_data', 'Download air quality data'),
    ('configure_alerts', 'Configure personal alerts'),
    ('generate_reports', 'Generate custom reports'),
    ('manage_users', 'Manage user accounts'),
    ('manage_stations', 'Manage monitoring stations'),
    ('system_configuration', 'Configure system settings');

-- Assign permissions to roles (example)
INSERT INTO RolePermission (role_id, permission_id)
SELECT r.id, p.id
FROM Role r
CROSS JOIN Permission p
WHERE 
    (r.name = 'Citizen' AND p.name IN ('view_current_aqi', 'configure_alerts')) OR
    (r.name = 'Researcher' AND p.name IN ('view_current_aqi', 'view_historical_data', 'download_data', 'configure_alerts', 'generate_reports')) OR
    (r.name = 'Administrator');

-- Insert common pollutants
INSERT INTO Pollutant (name, unit, description) VALUES
    ('PM2.5', 'μg/m³', 'Fine particulate matter with diameter less than 2.5 micrometers'),
    ('PM10', 'μg/m³', 'Particulate matter with diameter less than 10 micrometers'),
    ('O3', 'ppb', 'Ground-level ozone'),
    ('NO2', 'ppb', 'Nitrogen dioxide'),
    ('SO2', 'ppb', 'Sulfur dioxide'),
    ('CO', 'ppm', 'Carbon monoxide');

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE Station IS 'Physical monitoring stations that collect air quality data';
COMMENT ON TABLE Provider IS 'External data providers and their API configurations';
COMMENT ON TABLE AirQualityReading IS 'Individual air quality measurements from stations';
COMMENT ON TABLE Pollutant IS 'Types of air pollutants being monitored';
COMMENT ON TABLE MapRegion IS 'Geographic regions for spatial analysis';
COMMENT ON TABLE AppUser IS 'Application users with authentication credentials';
COMMENT ON TABLE Role IS 'User roles defining access levels';
COMMENT ON TABLE Permission IS 'Granular permissions that can be assigned to roles';
COMMENT ON TABLE RolePermission IS 'Junction table mapping roles to permissions';
COMMENT ON TABLE Alert IS 'User-configured alerts for air quality thresholds';
COMMENT ON TABLE Recommendation IS 'Personalized health recommendations based on AQI';
COMMENT ON TABLE ProductRecommendation IS 'Product suggestions for health protection';
COMMENT ON TABLE Report IS 'Generated reports for data analysis';
COMMENT ON TABLE AirQualityDailyStats IS 'Pre-aggregated daily statistics for performance';

COMMENT ON COLUMN AirQualityReading.raw_json IS 'Raw API payload stored for audit trail and reprocessing';
COMMENT ON COLUMN Alert.threshold IS 'AQI or concentration value that triggers the alert';
COMMENT ON COLUMN Recommendation.aqi_band IS 'EPA AQI band: 0=Good, 1=Moderate, 2=USG, 3=Unhealthy, 4=VeryUnhealthy, 5=Hazardous';
