"""
Database initialization script
Seeds initial data: roles, permissions, pollutants
Run this after the database schema is created
"""

from sqlalchemy.orm import Session
from database.postgres_db import SessionLocal, engine, Base
from models import Role, Permission, RolePermission, Pollutant, Provider, Station, MapRegion

def init_database():
    """Initialize database with seed data"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if providers and stations already exist
        provider_count = db.query(Provider).count()
        station_count = db.query(Station).count()
        
        if provider_count > 0 and station_count > 0:
            print(f"Database already initialized ({provider_count} providers, {station_count} stations).")
            return
        
        print(f"Initializing database... (providers: {provider_count}, stations: {station_count})")
        
        print("Seeding initial data...")
        
        # Insert roles only if they don't exist
        roles = db.query(Role).all()
        if len(roles) == 0:
            roles_data = [
                {"name": "Citizen", "description": "General public user with basic access"},
                {"name": "Researcher", "description": "Academic or scientific researcher with extended access"},
                {"name": "Administrator", "description": "System administrator with full access"}
            ]
            
            roles = []
            for role_data in roles_data:
                role = Role(**role_data)
                db.add(role)
                roles.append(role)
            
            db.flush()
            print(f"Created {len(roles)} roles")
        else:
            print(f"Roles already exist ({len(roles)} roles found)")
        
        # Insert permissions only if they don't exist
        permissions = db.query(Permission).all()
        if len(permissions) == 0:
            permissions_data = [
                {"name": "view_current_aqi", "description": "View current air quality index"},
                {"name": "view_historical_data", "description": "View historical air quality data"},
                {"name": "download_data", "description": "Download air quality data"},
                {"name": "configure_alerts", "description": "Configure personal alerts"},
                {"name": "generate_reports", "description": "Generate custom reports"},
                {"name": "manage_users", "description": "Manage user accounts"},
                {"name": "manage_stations", "description": "Manage monitoring stations"},
                {"name": "system_configuration", "description": "Configure system settings"}
            ]
            
            permissions = []
            for perm_data in permissions_data:
                perm = Permission(**perm_data)
                db.add(perm)
                permissions.append(perm)
            
            db.flush()
            print(f"Created {len(permissions)} permissions")
            
            # Assign permissions to roles
            role_permissions_map = {
                "Citizen": ["view_current_aqi", "configure_alerts"],
                "Researcher": ["view_current_aqi", "view_historical_data", "download_data", "configure_alerts", "generate_reports"],
                "Administrator": None  # All permissions
            }
            
            for role in roles:
                perms = role_permissions_map.get(role.name)
                
                if perms is None:
                    # Administrator gets all permissions
                    for perm in permissions:
                        role_perm = RolePermission(role_id=role.id, permission_id=perm.id)
                        db.add(role_perm)
                else:
                    # Assign specific permissions
                    for perm_name in perms:
                        perm = next((p for p in permissions if p.name == perm_name), None)
                        if perm:
                            role_perm = RolePermission(role_id=role.id, permission_id=perm.id)
                            db.add(role_perm)
            
            print("Assigned permissions to roles")
        else:
            print(f"Permissions already exist ({len(permissions)} permissions found)")
        
        # Insert pollutants only if they don't exist
        existing_pollutants = db.query(Pollutant).all()
        if len(existing_pollutants) == 0:
            pollutants_data = [
                {"name": "PM2.5", "unit": "μg/m³", "description": "Fine particulate matter with diameter less than 2.5 micrometers"},
                {"name": "PM10", "unit": "μg/m³", "description": "Particulate matter with diameter less than 10 micrometers"},
                {"name": "O3", "unit": "ppb", "description": "Ground-level ozone"},
                {"name": "NO2", "unit": "ppb", "description": "Nitrogen dioxide"},
                {"name": "SO2", "unit": "ppb", "description": "Sulfur dioxide"},
                {"name": "CO", "unit": "ppm", "description": "Carbon monoxide"}
            ]
            
            for poll_data in pollutants_data:
                pollutant = Pollutant(**poll_data)
                db.add(pollutant)
            
            print(f"Created {len(pollutants_data)} pollutants")
        else:
            print(f"Pollutants already exist ({len(existing_pollutants)} pollutants found)")
        
        # Insert default providers (mock)
        providers_data = [
            {"name": "AQICN Mock", "api_endpoint": "https://api.waqi.info/feed/", "ingestion_frequency_minutes": 30},
            {"name": "Google Air Quality Mock", "api_endpoint": "https://airquality.googleapis.com/v1/", "ingestion_frequency_minutes": 30},
            {"name": "IQAir Mock", "api_endpoint": "https://api.airvisual.com/v2/", "ingestion_frequency_minutes": 60}
        ]
        
        for prov_data in providers_data:
            provider = Provider(**prov_data)
            db.add(provider)
        
        print(f"Created {len(providers_data)} providers")
        
        # Insert map regions using raw SQL to avoid geom type issues
        regions_data = [
            {"name": "Bogotá D.C.", "description": "Capital city of Colombia"},
            {"name": "Antioquia", "description": "Department of Antioquia"},
            {"name": "Valle del Cauca", "description": "Department of Valle del Cauca"}
        ]
        
        from sqlalchemy import text
        for region_data in regions_data:
            db.execute(
                text("INSERT INTO mapregion (name, description) VALUES (:name, :description)"),
                {"name": region_data["name"], "description": region_data["description"]}
            )
        
        db.flush()
        
        # Load created regions
        regions = db.query(MapRegion).all()
        print(f"Created {len(regions)} regions")
        
        # Insert monitoring stations
        providers = db.query(Provider).all()
        provider_aqicn = next((p for p in providers if "AQICN" in p.name), providers[0])
        provider_google = next((p for p in providers if "Google" in p.name), providers[1])
        provider_iqair = next((p for p in providers if "IQAir" in p.name), providers[2])
        
        stations_data = [
            {
                "name": "Kennedy - Bogotá",
                "latitude": 4.6097,
                "longitude": -74.0817,
                "city": "Bogotá",
                "country": "Colombia",
                "region_id": regions[0].id,
                "provider_id": provider_aqicn.id
            },
            {
                "name": "Usaquén - Bogotá",
                "latitude": 4.7110,
                "longitude": -74.0721,
                "city": "Bogotá",
                "country": "Colombia",
                "region_id": regions[0].id,
                "provider_id": provider_google.id
            },
            {
                "name": "Medellín Centro",
                "latitude": 6.2442,
                "longitude": -75.5812,
                "city": "Medellín",
                "country": "Colombia",
                "region_id": regions[1].id,
                "provider_id": provider_iqair.id
            },
            {
                "name": "Envigado - Medellín",
                "latitude": 6.1650,
                "longitude": -75.5847,
                "city": "Medellín",
                "country": "Colombia",
                "region_id": regions[1].id,
                "provider_id": provider_aqicn.id
            },
            {
                "name": "Cali Centro",
                "latitude": 3.4516,
                "longitude": -76.5320,
                "city": "Cali",
                "country": "Colombia",
                "region_id": regions[2].id,
                "provider_id": provider_google.id
            }
        ]
        
        for station_data in stations_data:
            station = Station(**station_data)
            db.add(station)
        
        print(f"Created {len(stations_data)} monitoring stations")
        
        # Commit all changes
        db.commit()
        print("✓ Database initialization complete!")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
