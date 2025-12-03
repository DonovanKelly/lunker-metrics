from open_meteo import fetch_weather_data
from geoloc import get_coordinates
import pandas as pd
from pathlib import Path
import time
import pickle
import os
from tqdm import tqdm

def get_lunker_data(file: Path) -> pd.DataFrame:
    # Read the CSV, skipping the first row if it's a title
    df = pd.read_csv(file, skiprows=1)
    # Normalize column names: strip spaces and make lower case for consistency
    df.columns = df.columns.str.strip().str.lower()
    # Parse date
    if 'date' in df.columns:
        df['date_str'] = pd.to_datetime(df['date'], format='%m/%d/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    else:
        # Fallback to month, day, year
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        if all(col in df.columns for col in ['month', 'day', 'year']):
            df['month_num'] = df['month'].str.lower().map(month_map)
            df['date_str'] = df['year'].astype(str) + '-' + df['month_num'].astype(str).str.zfill(2) + '-' + df[
                'day'].astype(str).str.zfill(2)
            df = df.drop(columns=['month_num'])
    return df

def get_lat_long(cache: Path, df: pd.DataFrame) -> pd.DataFrame:
    unique_locations = df[['lake_name']].drop_duplicates().reset_index(drop=True)
    unique_locations['lat'] = None
    unique_locations['lon'] = None
    # Load existing geocode_dict if cache exists
    if os.path.exists(cache):
        with open(cache, 'rb') as f:
            geocode_dict = pickle.load(f)
        print(f"Loaded geocode cache with {len(geocode_dict)} entries")
    else:
        geocode_dict = {}
    # Counter for saving every few iterations
    save_interval = 10  # Save every 10 fetches
    fetch_count = 0
    for idx, row in tqdm(unique_locations.iterrows(), total=len(unique_locations)):
        lake_name = row['lake_name']
        if lake_name in geocode_dict:
            if geocode_dict[lake_name] is None:
                geocode_dict[lake_name] = (None, None)
            lat, lon = geocode_dict[lake_name]
            unique_locations.at[idx, 'lat'] = lat
            unique_locations.at[idx, 'lon'] = lon
            continue
        try:
            lat, lon = get_coordinates(str(lake_name))
            unique_locations.at[idx, 'lat'] = lat
            unique_locations.at[idx, 'lon'] = lon
            geocode_dict[lake_name] = (lat, lon)
            fetch_count += 1
            if fetch_count % save_interval == 0:
                with open(cache, 'wb') as f:
                    pickle.dump(geocode_dict, f)
                print(f"Saved geocode cache after {fetch_count} fetches")
        except Exception:
            geocode_dict[lake_name] = (None, None)
            print(f"Failed to geocode {lake_name}")
        time.sleep(1)  # Respect geocoder rate limits
    # Save final geocode cache
    with open(cache, 'wb') as f:
        pickle.dump(geocode_dict, f)

    print("Saved final geocode cache")
    # Merge lat/long back to original df
    return df.merge(unique_locations[['lake_name', 'lat', 'lon']], on=['lake_name'], how='left')

def get_openmeteo_weather_data(cache: Path, df: pd.DataFrame) -> pd.DataFrame:
    # Get unique weather needs (lat, lon, date_str)
    unique_weather = df[['lat', 'lon', 'date_str']].drop_duplicates().dropna(subset=['lat', 'lon']).reset_index(drop=True)
    # Load existing weather_dict if cache exists
    if os.path.exists(cache):
        with open(cache, 'rb') as f:
            weather_dict = pickle.load(f)
        print(f"Loaded existing cache with {len(weather_dict)} entries")
    else:
        weather_dict = {}
    # Counter for saving every few iterations
    save_interval = 10 # Save every 10 fetches
    fetch_count = 0
    for idx, row in tqdm(unique_weather.iterrows(), total=len(unique_weather)):
        lat = row['lat']
        lon = row['lon']
        if lat is None or lon is None:
            continue
        date = row['date_str']
        key = (lat, lon, date)
        if key in weather_dict:
            continue
        try:
            hourly_df = fetch_weather_data(lat, lon, date)
            # Simply select the 12th row (0-based index 11 for 11:00 UTC or 12 for 12:00; assuming 12:00 UTC as noon approximation)
            if len(hourly_df) >= 13:
                noon_row = hourly_df.iloc[12] # 12:00 UTC
                weather_data = {
                    'noon_temperature_2m': noon_row['temperature_2m'],
                    'noon_cloud_cover': noon_row['cloud_cover'],
                    'noon_rain': noon_row['rain'],
                    'noon_snowfall': noon_row['snowfall'],
                    'noon_surface_pressure': noon_row['surface_pressure'],
                    'noon_pressure_msl': noon_row['pressure_msl'],
                    'noon_wind_speed_10m': noon_row['wind_speed_10m']
                }
                weather_dict[key] = weather_data
                fetch_count += 1
                if fetch_count % save_interval == 0:
                    with open(cache, 'wb') as f:
                        pickle.dump(weather_dict, f)
                    print(f"Saved cache after {fetch_count} fetches")
            else:
                print(f"Insufficient data for {lat}, {lon} on {date}")
        except Exception as e:
            print(f"Failed to fetch weather for {lat}, {lon} on {date}: {e}")
        time.sleep(0.1)
    # Save final cache
    with open(cache, 'wb') as f:
        pickle.dump(weather_dict, f)
    print("Saved final cache")
    # Add weather columns to df
    weather_columns = ['noon_temperature_2m', 'noon_cloud_cover', 'noon_rain', 'noon_snowfall',
                       'noon_surface_pressure', 'noon_pressure_msl', 'noon_wind_speed_10m']
    for col in weather_columns:
        df[col] = None
    for idx, row in df.iterrows():
        if pd.notna(row['lat']) and pd.notna(row['lon']) and pd.notna(row['date_str']):
            key = (row['lat'], row['lon'], row['date_str'])
            if key in weather_dict:
                for col in weather_columns:
                    df.at[idx, col] = weather_dict[key][col]
    # Drop temporary date_str if not needed
    return df.drop(columns=['date_str'], errors='ignore')



if __name__ == "__main__":
    file_path = Path("./sharelunker_raw_data_2025-07-13_2143.csv")
    df = get_lunker_data(file_path)
    df = get_lat_long(file_path.parent / 'geocode_cache.pkl', df)
    df = get_openmeteo_weather_data(file_path.parent / 'weather_cache.pkl', df)
    # Save the updated data
    output_path = file_path.parent / 'sharelunker_with_weather_test.csv'
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")
