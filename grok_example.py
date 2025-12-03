import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import time


# Function to round datetime to nearest hour
def round_to_nearest_hour(dt):
    if dt.minute >= 30:
        dt = dt + timedelta(hours=1)
    return dt.replace(minute=0, second=0, microsecond=0)

# Initialize geocoder
geolocator = Nominatim(user_agent="lake_weather_app")

# Sample input: list of lakes and corresponding timestamps
# User can edit these lists
lakes = ["Lake Travis", "Lake Buchanan", "Canyon Lake"]
timestamps = ["2023-06-15 14:30", "2023-07-01 10:15", "2024-01-20 16:45"]

# Ensure lists are the same length
if len(lakes) != len(timestamps):
    raise ValueError("Lakes and timestamps lists must be the same length")

results = []

for lake, timestamp_str in zip(lakes, timestamps):
    # Geocode the lake
    query = f"{lake}, Texas"
    location = geolocator.geocode(query)
    if not location:
        print(f"Could not geocode {lake}")
        continue
    lat = location.latitude
    lon = location.longitude

    # Parse timestamp
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print(f"Invalid timestamp format for {timestamp_str}. Expected YYYY-MM-DD HH:MM")
        continue

    # Round to nearest hour
    rounded_dt = round_to_nearest_hour(dt)
    date = rounded_dt.strftime("%Y-%m-%d")
    target_time = rounded_dt.strftime("%Y-%m-%dT%H:00")

    # Build API URL
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&"
        f"start_date={date}&end_date={date}&"
        f"hourly=temperature_2m,wind_speed_10m,pressure_msl"
    )

    # Fetch data
    response = requests.get(url)
    if response.status_code != 200:
        print(f"API request failed for {lake} on {date}")
        continue

    data = response.json().get('hourly')
    if not data:
        print(f"No data returned for {lake} on {date}")
        continue

    # Find the index for the target time
    try:
        index = data['time'].index(target_time)
    except ValueError:
        print(f"Target time {target_time} not found in data for {lake}")
        continue

    # Extract values
    temp = data['temperature_2m'][index]
    wind_speed = data['wind_speed_10m'][index]
    pressure = data['pressure_msl'][index]

    # Store result
    results.append({
        'lake': lake,
        'timestamp': timestamp_str,
        'rounded_time': target_time,
        'temperature_c': temp,
        'wind_speed_kmh': wind_speed,
        'barometric_pressure_hpa': pressure
    })

    # Respect Nominatim rate limit
    time.sleep(1)

# Output results
if results:
    print("Weather Data:")
    for res in results:
        print(f"Lake: {res['lake']}")
        print(f"Timestamp: {res['timestamp']} (rounded to {res['rounded_time']})")
        print(f"Temperature: {res['temperature_c']} °C")
        print(f"Wind Speed: {res['wind_speed_kmh']} km/h")
        print(f"Barometric Pressure: {res['barometric_pressure_hpa']} hPa")
        print("---")
else:
    print("No data retrieved.")