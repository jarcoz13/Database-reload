#!/bin/bash

##############################################################################
# Validation Script - Air Quality Monitoring System
# Validates the complete setup: DB initialization, API, CORS, and data flow
##############################################################################

set -e  # Exit on error

echo "=================================="
echo "Air Quality System Validation"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if containers are running
echo "1. Checking Docker containers..."
POSTGRES_RUNNING=$(docker ps --filter "name=airquality_postgres" --format "{{.Status}}" | grep -c "Up" || true)
MONGO_RUNNING=$(docker ps --filter "name=airquality_mongodb" --format "{{.Status}}" | grep -c "Up" || true)
BACKEND_RUNNING=$(docker ps --filter "name=airquality_backend" --format "{{.Status}}" | grep -c "Up" || true)
FRONTEND_RUNNING=$(docker ps --filter "name=airquality_frontend" --format "{{.Status}}" | grep -c "Up" || true)

print_status $POSTGRES_RUNNING "PostgreSQL container"
print_status $MONGO_RUNNING "MongoDB container"
print_status $BACKEND_RUNNING "Backend container"
print_status $FRONTEND_RUNNING "Frontend container"
echo ""

# Check database initialization
echo "2. Checking database initialization..."

# Check roles
ROLES_COUNT=$(docker exec airquality_postgres psql -U airquality_user -d airquality_db -t -c "SELECT COUNT(*) FROM role;" 2>/dev/null | tr -d ' \n' || echo "0")
print_status $([ "$ROLES_COUNT" -gt 0 ] && echo 0 || echo 1) "Roles table ($ROLES_COUNT roles)"

# Check pollutants
POLLUTANTS_COUNT=$(docker exec airquality_postgres psql -U airquality_user -d airquality_db -t -c "SELECT COUNT(*) FROM pollutant;" 2>/dev/null | tr -d ' \n' || echo "0")
print_status $([ "$POLLUTANTS_COUNT" -gt 0 ] && echo 0 || echo 1) "Pollutants table ($POLLUTANTS_COUNT pollutants)"

# Check providers
PROVIDERS_COUNT=$(docker exec airquality_postgres psql -U airquality_user -d airquality_db -t -c "SELECT COUNT(*) FROM provider;" 2>/dev/null | tr -d ' \n' || echo "0")
print_status $([ "$PROVIDERS_COUNT" -gt 0 ] && echo 0 || echo 1) "Providers table ($PROVIDERS_COUNT providers)"

# Check stations
STATIONS_COUNT=$(docker exec airquality_postgres psql -U airquality_user -d airquality_db -t -c "SELECT COUNT(*) FROM station;" 2>/dev/null | tr -d ' \n' || echo "0")
print_status $([ "$STATIONS_COUNT" -gt 0 ] && echo 0 || echo 1) "Stations table ($STATIONS_COUNT stations)"

# Check test users
USERS_COUNT=$(docker exec airquality_postgres psql -U airquality_user -d airquality_db -t -c "SELECT COUNT(*) FROM appuser WHERE username LIKE 'testuser%';" 2>/dev/null | tr -d ' \n' || echo "0")
print_status $([ "$USERS_COUNT" -gt 0 ] && echo 0 || echo 1) "Test users ($USERS_COUNT users)"

echo ""

# Check API endpoints
echo "3. Checking API endpoints..."

# Health check
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
print_status $([ "$HEALTH_STATUS" = "200" ] && echo 0 || echo 1) "Health endpoint (HTTP $HEALTH_STATUS)"

# API info
API_INFO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/info 2>/dev/null || echo "000")
print_status $([ "$API_INFO_STATUS" = "200" ] && echo 0 || echo 1) "API info endpoint (HTTP $API_INFO_STATUS)"

# Stations endpoint
STATIONS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/stations 2>/dev/null || echo "000")
print_status $([ "$STATIONS_STATUS" = "200" ] && echo 0 || echo 1) "Stations endpoint (HTTP $STATIONS_STATUS)"

# Alerts endpoint (GET)
ALERTS_GET_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/alerts?user_id=1" 2>/dev/null || echo "000")
print_status $([ "$ALERTS_GET_STATUS" = "200" ] && echo 0 || echo 1) "Alerts GET endpoint (HTTP $ALERTS_GET_STATUS)"

echo ""

# Check CORS
echo "4. Checking CORS configuration..."
CORS_RESPONSE=$(curl -s -I -H "Origin: http://localhost:5173" http://localhost:8000/api/stations 2>/dev/null | grep -i "access-control-allow-origin" || echo "")

if [ -n "$CORS_RESPONSE" ]; then
    print_status 0 "CORS headers present"
    print_info "   $CORS_RESPONSE"
else
    print_status 1 "CORS headers missing"
fi

echo ""

# Check data ingestion
echo "5. Checking data ingestion..."
READINGS_COUNT=$(docker exec airquality_postgres psql -U airquality_user -d airquality_db -t -c "SELECT COUNT(*) FROM airqualityreading;" 2>/dev/null | tr -d ' \n' || echo "0")

if [ "$READINGS_COUNT" -gt 0 ]; then
    print_status 0 "Data ingestion working ($READINGS_COUNT readings)"
    
    # Check latest reading
    LATEST_READING=$(docker exec airquality_postgres psql -U airquality_user -d airquality_db -t -c "SELECT datetime FROM airqualityreading ORDER BY datetime DESC LIMIT 1;" 2>/dev/null | tr -d '\n' || echo "")
    if [ -n "$LATEST_READING" ]; then
        print_info "   Latest reading: $LATEST_READING"
    fi
else
    print_status 1 "No readings found (ingestion may not have run yet)"
    print_info "   Wait a few minutes and check again"
fi

echo ""

# Check frontend
echo "6. Checking frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 2>/dev/null || echo "000")
print_status $([ "$FRONTEND_STATUS" = "200" ] && echo 0 || echo 1) "Frontend accessible (HTTP $FRONTEND_STATUS)"

echo ""

# Summary
echo "=================================="
echo "Validation Summary"
echo "=================================="
echo ""

if [ "$POSTGRES_RUNNING" -eq 1 ] && [ "$BACKEND_RUNNING" -eq 1 ] && [ "$FRONTEND_RUNNING" -eq 1 ] && \
   [ "$ROLES_COUNT" -gt 0 ] && [ "$STATIONS_COUNT" -gt 0 ] && [ "$USERS_COUNT" -gt 0 ] && \
   [ "$HEALTH_STATUS" = "200" ] && [ -n "$CORS_RESPONSE" ]; then
    echo -e "${GREEN}✓ System is properly configured and running!${NC}"
    echo ""
    echo "Access points:"
    echo "  - Frontend:  http://localhost:5173"
    echo "  - Backend:   http://localhost:8000"
    echo "  - API Docs:  http://localhost:8000/docs"
    echo "  - PgAdmin:   http://localhost:5050"
else
    echo -e "${YELLOW}⚠ Some components may need attention${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  - Check logs: docker-compose logs -f [service]"
    echo "  - Restart:    docker-compose restart"
    echo "  - Reinit DB:  docker-compose exec backend python init_db.py"
fi

echo ""
