import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# example: https://open-meteo.com/en/docs/historical-weather-api?start_date=2025-08-09&end_date=2025-08-09&hourly=temperature_2m,cloud_cover,rain,snowfall,surface_pressure,pressure_msl,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def fetch_weather_data(lat: float, lon: float, date: str):
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
    	"latitude": lat,
    	"longitude": lon,
    	"start_date": date,
    	"end_date": date,
    	"hourly": ["temperature_2m", "cloud_cover", "rain", "snowfall", "surface_pressure", "pressure_msl", "wind_speed_10m"],
    	"temperature_unit": "fahrenheit",
    	"wind_speed_unit": "mph",
    	"precipitation_unit": "inch",
        "timezone": "America/Chicago",
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()
    hourly_rain = hourly.Variables(2).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(3).ValuesAsNumpy()
    hourly_surface_pressure = hourly.Variables(4).ValuesAsNumpy()
    hourly_pressure_msl = hourly.Variables(5).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(6).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
    	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
    	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
    	freq = pd.Timedelta(seconds = hourly.Interval()),
    	inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["rain"] = hourly_rain
    hourly_data["snowfall"] = hourly_snowfall
    hourly_data["surface_pressure"] = hourly_surface_pressure
    hourly_data["pressure_msl"] = hourly_pressure_msl
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    return hourly_dataframe


# Example usage
if __name__ == "__main__":
    # Example parameters (Chicago on January 1, 2023)
    lat = 41.8781
    lon = -87.6298
    date = "2023-01-01"

    try:
        data = fetch_weather_data(lat, lon, date)
        print(data)
    except ValueError as e:
        print(e)