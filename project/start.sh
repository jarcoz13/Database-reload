#!/bin/bash

# Quick Start Script for Air Quality Platform
# This script starts the entire platform and performs basic verification

echo "🌍 Air Quality Platform - Quick Start"
echo "======================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check for port conflicts
echo "🔍 Checking for port conflicts..."
PORTS_IN_USE=""
for port in 5432 27017 8000 5173 5050 8081; do
    if lsof -i :$port > /dev/null 2>&1; then
        PORTS_IN_USE="$PORTS_IN_USE $port"
    fi
done

if [ ! -z "$PORTS_IN_USE" ]; then
    echo "⚠️  Warning: The following ports are already in use:$PORTS_IN_USE"
    echo "   This may cause conflicts. Consider stopping other services."
    echo ""
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted."
        exit 1
    fi
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose down 2>&1 | grep -v "WARN\[0000\]"

# Start services
echo "🚀 Starting all services..."
if ! docker compose up -d --build 2>&1 | grep -v "WARN\[0000\]"; then
    echo ""
    echo "❌ Error: Failed to start services. Check the logs above."
    echo "   Common issues:"
    echo "   • Port conflicts (use: docker compose down -v)"
    echo "   • Docker resources (restart Docker Desktop)"
    echo ""
    exit 1
fi

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check service health
echo ""
echo "🏥 Checking service health..."
echo ""

# Check PostgreSQL
echo -n "PostgreSQL: "
if docker compose exec -T postgres pg_isready -U airquality_user > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not ready"
fi

# Check MongoDB
echo -n "MongoDB: "
if docker compose exec -T mongodb mongosh --quiet --eval "db.runCommand('ping').ok" > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not ready"
fi

# Check Backend
echo -n "Backend API: "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not ready (may still be starting...)"
fi

# Check Frontend
echo -n "Frontend: "
if curl -s http:/ 2>&1 | grep -v "WARN\[0000\]"

# Check if backend and frontend are running
BACKEND_RUNNING=$(docker compose ps | grep airquality_backend | grep -c "Up")
FRONTEND_RUNNING=$(docker compose ps | grep airquality_frontend | grep -c "Up")

if [ "$BACKEND_RUNNING" -eq "0" ]; then
    echo ""
    echo "⚠️  Backend failed to start. Checking logs..."
    docker compose logs --tail=20 backend
    echo ""
fi

if [ "$FRONTEND_RUNNING" -eq "0" ]; then
    echo ""
    echo "⚠️  Frontend failed to start. Checking logs..."
    docker compose logs --tail=20 frontend
    echo ""
fi

echo ""
if [ "$BACKEND_RUNNING" -gt "0" ] && [ "$FRONTEND_RUNNING" -gt "0" ]; then
    echo "🎉 Platform is running successfully!"
else
    echo "⚠️  Platform started with some issues. Check logs above."
fi

echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "🎉 Platform is starting up!"
echo ""
echo "📍 Access Points:"
echo "   • Frontend:        http://localhost:5173"
echo "   • Backend API:     http://localhost:8000"
echo "   • API Docs:        http://localhost:8000/docs"
echo "   • PgAdmin:         http://localhost:5050"
echo "   • Mongo Express:   http://localhost:8081"
echo ""
echo "🧪 Quick Tests:"
echo "   • Health Check:    curl http://localhost:8000/health"
echo "   • Pollutants:      curl http://localhost:8000/api/pollutants"
echo "   • Admin Health:    curl http://localhost:8000/admin/health"
echo "   • Trigger Job:     curl -X POST http://localhost:8000/admin/jobs/run/ingestion"
echo ""
echo "📚 Documentation:"
echo "   • README:          project/README.md"
echo "   • Architecture:    project/back/ARCHITECTURE.md"
echo "   • Testing Guide:   project/TESTING.md"
echo "   • Compliance:      project/ARCHITECTURE_COMPLIANCE.md"
echo ""
echo "📋 Useful Commands:"
echo "   • View logs:       docker compose logs -f [service]"
echo "   • Stop:            docker compose down"
echo "   • Restart:         docker compose restart [service]"
echo "   • Clean restart:   docker compose down -v && docker compose up -d"
echo ""
echo "✨ Happy coding!"
