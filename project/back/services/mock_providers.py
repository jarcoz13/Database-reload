"""
Mock services for external air quality data providers
According to architecture: AQICN, Google Air Quality API, IQAir

These mocks simulate external API responses for development/testing
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


class AQICNMockService:
    """Mock service for AQICN (Air Quality Index China Network) API"""
    
    def __init__(self):
        self.base_url = "https://api.waqi.info/feed/"
        self.cities = ["bogota", "medellin", "cali", "barranquilla", "cartagena"]
        
    def get_station_data(self, city: str) -> Dict[str, Any]:
        """
        Simulate AQICN API response for a city
        Returns mock air quality data
        """
        return {
            "status": "ok",
            "data": {
                "aqi": random.randint(20, 180),
                "idx": random.randint(1000, 9999),
                "city": {
                    "name": city.capitalize(),
                    "geo": self._get_mock_coordinates(city),
                },
                "time": {
                    "s": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "tz": "-05:00",
                },
                "iaqi": {
                    "pm25": {"v": random.uniform(10, 150)},
                    "pm10": {"v": random.uniform(20, 200)},
                    "o3": {"v": random.uniform(10, 100)},
                    "no2": {"v": random.uniform(5, 80)},
                    "so2": {"v": random.uniform(2, 40)},
                    "co": {"v": random.uniform(0.3, 2.5)},
                }
            }
        }
    
    def get_all_stations(self) -> List[Dict[str, Any]]:
        """Get mock data for all cities"""
        return [self.get_station_data(city) for city in self.cities]
    
    def _get_mock_coordinates(self, city: str) -> List[float]:
        """Return mock coordinates for Colombian cities"""
        coords = {
            "bogota": [4.6097, -74.0817],
            "medellin": [6.2442, -75.5812],
            "cali": [3.4516, -76.5320],
            "barranquilla": [10.9639, -74.7964],
            "cartagena": [10.3910, -75.4794],
        }
        return coords.get(city.lower(), [4.0, -74.0])


class GoogleAirQualityMockService:
    """Mock service for Google Air Quality API"""
    
    def __init__(self):
        self.base_url = "https://airquality.googleapis.com/v1/"
        
    def get_current_conditions(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Simulate Google Air Quality API response
        """
        return {
            "dateTime": datetime.utcnow().isoformat() + "Z",
            "regionCode": "CO",
            "indexes": [
                {
                    "code": "uaqi",
                    "displayName": "Universal AQI",
                    "aqi": random.randint(20, 150),
                    "aqiDisplay": self._get_aqi_display(random.randint(20, 150)),
                    "color": self._get_aqi_color(random.randint(20, 150)),
                    "category": self._get_aqi_category(random.randint(20, 150)),
                }
            ],
            "pollutants": [
                {
                    "code": "pm25",
                    "displayName": "PM2.5",
                    "fullName": "Fine particulate matter (<2.5µm)",
                    "concentration": {"value": random.uniform(10, 100), "units": "MICROGRAMS_PER_CUBIC_METER"},
                    "additionalInfo": {
                        "sources": "Main sources: vehicle emissions, wood burning",
                        "effects": "Penetrates deep into lungs and bloodstream",
                    }
                },
                {
                    "code": "pm10",
                    "displayName": "PM10",
                    "concentration": {"value": random.uniform(20, 150), "units": "MICROGRAMS_PER_CUBIC_METER"},
                },
                {
                    "code": "o3",
                    "displayName": "Ozone",
                    "concentration": {"value": random.uniform(20, 120), "units": "PARTS_PER_BILLION"},
                },
                {
                    "code": "no2",
                    "displayName": "Nitrogen dioxide",
                    "concentration": {"value": random.uniform(10, 80), "units": "PARTS_PER_BILLION"},
                }
            ],
            "healthRecommendations": {
                "generalPopulation": self._get_health_recommendation("general"),
                "elderly": self._get_health_recommendation("elderly"),
                "children": self._get_health_recommendation("children"),
                "athletes": self._get_health_recommendation("athletes"),
            }
        }
    
    def _get_aqi_display(self, aqi: int) -> str:
        if aqi <= 50: return "Good"
        elif aqi <= 100: return "Moderate"
        elif aqi <= 150: return "Unhealthy for Sensitive Groups"
        elif aqi <= 200: return "Unhealthy"
        elif aqi <= 300: return "Very Unhealthy"
        else: return "Hazardous"
    
    def _get_aqi_color(self, aqi: int) -> Dict[str, float]:
        if aqi <= 50: return {"red": 0, "green": 228/255, "blue": 0}
        elif aqi <= 100: return {"red": 255/255, "green": 255/255, "blue": 0}
        elif aqi <= 150: return {"red": 255/255, "green": 126/255, "blue": 0}
        elif aqi <= 200: return {"red": 255/255, "green": 0, "blue": 0}
        elif aqi <= 300: return {"red": 143/255, "green": 63/255, "blue": 151/255}
        else: return {"red": 126/255, "green": 0, "blue": 35/255}
    
    def _get_aqi_category(self, aqi: int) -> str:
        if aqi <= 50: return "Excellent air quality"
        elif aqi <= 100: return "Acceptable air quality"
        elif aqi <= 150: return "Air quality adequate for most people"
        elif aqi <= 200: return "Air quality may begin to affect everyone"
        elif aqi <= 300: return "Health warnings of emergency conditions"
        else: return "Health alert: everyone may experience serious effects"
    
    def _get_health_recommendation(self, group: str) -> str:
        recommendations = {
            "general": "Enjoy outdoor activities.",
            "elderly": "Consider reducing prolonged outdoor exertion.",
            "children": "Children can play outside.",
            "athletes": "No restrictions on training outdoors.",
        }
        return recommendations.get(group, "No specific recommendations.")


class IQAirMockService:
    """Mock service for IQAir API"""
    
    def __init__(self):
        self.base_url = "https://api.airvisual.com/v2/"
        
    def get_city_data(self, city: str, country: str = "Colombia") -> Dict[str, Any]:
        """
        Simulate IQAir API response for a city
        """
        aqi = random.randint(20, 180)
        return {
            "status": "success",
            "data": {
                "city": city,
                "state": self._get_state(city),
                "country": country,
                "location": {
                    "type": "Point",
                    "coordinates": self._get_coordinates(city),
                },
                "current": {
                    "weather": {
                        "ts": datetime.utcnow().isoformat() + "Z",
                        "tp": random.randint(18, 32),  # Temperature
                        "pr": random.randint(1010, 1020),  # Pressure
                        "hu": random.randint(40, 90),  # Humidity
                        "ws": random.uniform(0.5, 5.0),  # Wind speed
                        "wd": random.randint(0, 360),  # Wind direction
                    },
                    "pollution": {
                        "ts": datetime.utcnow().isoformat() + "Z",
                        "aqius": aqi,  # US AQI
                        "mainus": self._get_main_pollutant(aqi),
                        "aqicn": int(aqi * 0.9),  # China AQI
                        "maincn": self._get_main_pollutant(aqi),
                    }
                }
            }
        }
    
    def get_nearest_station(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get nearest station data by coordinates"""
        return {
            "status": "success",
            "data": {
                "city": "Mock City",
                "state": "Mock State",
                "country": "Colombia",
                "location": {
                    "type": "Point",
                    "coordinates": [longitude, latitude],
                },
                "current": {
                    "pollution": {
                        "ts": datetime.utcnow().isoformat() + "Z",
                        "aqius": random.randint(20, 150),
                        "mainus": "pm25",
                    }
                }
            }
        }
    
    def _get_state(self, city: str) -> str:
        states = {
            "bogota": "Bogotá D.C.",
            "medellin": "Antioquia",
            "cali": "Valle del Cauca",
            "barranquilla": "Atlántico",
            "cartagena": "Bolívar",
        }
        return states.get(city.lower(), "Unknown")
    
    def _get_coordinates(self, city: str) -> List[float]:
        coords = {
            "bogota": [-74.0817, 4.6097],
            "medellin": [-75.5812, 6.2442],
            "cali": [-76.5320, 3.4516],
            "barranquilla": [-74.7964, 10.9639],
            "cartagena": [-75.4794, 10.3910],
        }
        return coords.get(city.lower(), [-74.0, 4.0])
    
    def _get_main_pollutant(self, aqi: int) -> str:
        if aqi < 50:
            return random.choice(["pm25", "pm10", "o3"])
        elif aqi < 100:
            return random.choice(["pm25", "pm10"])
        else:
            return "pm25"  # PM2.5 is typically the worst at high AQI


# =====================================================
# Mock Service Manager
# =====================================================

class MockServiceManager:
    """
    Manages all mock services and provides unified interface
    for data ingestion
    """
    
    def __init__(self):
        self.aqicn = AQICNMockService()
        self.google = GoogleAirQualityMockService()
        self.iqair = IQAirMockService()
        
    def get_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch mock data from all providers
        Returns data organized by provider
        """
        return {
            "aqicn": self.aqicn.get_all_stations(),
            "google": [
                self.google.get_current_conditions(4.6097, -74.0817),  # Bogotá
                self.google.get_current_conditions(6.2442, -75.5812),  # Medellín
            ],
            "iqair": [
                self.iqair.get_city_data("bogota"),
                self.iqair.get_city_data("medellin"),
                self.iqair.get_city_data("cali"),
            ]
        }
    
    def get_provider_data(self, provider: str, **kwargs) -> Any:
        """
        Get data from specific provider
        
        Args:
            provider: "aqicn", "google", or "iqair"
            **kwargs: Provider-specific parameters
        """
        if provider == "aqicn":
            city = kwargs.get("city")
            return self.aqicn.get_station_data(city) if city else self.aqicn.get_all_stations()
        elif provider == "google":
            lat = kwargs.get("latitude", 4.6097)
            lon = kwargs.get("longitude", -74.0817)
            return self.google.get_current_conditions(lat, lon)
        elif provider == "iqair":
            city = kwargs.get("city", "bogota")
            return self.iqair.get_city_data(city)
        else:
            raise ValueError(f"Unknown provider: {provider}")
