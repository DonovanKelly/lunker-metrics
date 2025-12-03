import pickle

import pandas as pd

# Read the CSV file
df = pd.read_csv('./asos/mslp_2024-01-01_to_2024-01-01.csv')

# Filter for unique stations and select the first occurrence of lat/lon for each
unique_stations = df.drop_duplicates(subset=['station'])[['station', 'lat', 'lon']]

# Create the dictionary: station -> (lat, lon)
station_map = {row['station']: (row['lat'], row['lon']) for _, row in unique_stations.iterrows()}

with open("station_lat_lon.pkl", "wb") as fp:
    pickle.dump(station_map, fp)
