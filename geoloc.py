from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="lake_weather_app")

def get_coordinates(location: str) -> tuple[float, float]:
    location_obj = geolocator.geocode(f"{location}, USA")
    if not location_obj:
        raise ValueError(f"Could not geocode {location}")
    lat = location_obj.latitude
    lon = location_obj.longitude
    return lat, lon