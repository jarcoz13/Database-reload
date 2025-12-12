"""
Database initialization script
Seeds initial data: roles, permissions, pollutants
Run this after the database schema is created
"""

from sqlalchemy.orm import Session
from database.postgres_db import SessionLocal, engine, Base
from models import Role, Permission, RolePermission, Pollutant, Provider

def init_database():
    """Initialize database with seed data"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if already initialized
        if db.query(Role).count() > 0:
            print("Database already initialized.")
            return
        
        print("Seeding initial data...")
        
        # Insert roles
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
        
        # Insert permissions
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
        
        # Insert pollutants
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
