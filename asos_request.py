import requests
import os


# https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?help
"""
Variable,Description
tmpf,"Air Temperature in Fahrenheit, typically at 2 meters."
dwpf,"Dew Point Temperature in Fahrenheit, typically at 2 meters."
relh,Relative Humidity in %.
drct,Wind Direction in degrees from true north.
sknt,Wind Speed in knots.
p01i,One hour precipitation for the period from the observation time to the time of the previous hourly precipitation reset (varies slightly by site; may include melted frozen precipitation). Values are in inches.
alti,Pressure altimeter in inches.
mslp,Sea Level Pressure in millibars.
vsby,Visibility in miles.
gust,Wind Gust in knots.
skyc1,Sky Level 1 Coverage.
skyc2,Sky Level 2 Coverage.
skyc3,Sky Level 3 Coverage.
skyc4,Sky Level 4 Coverage.
skyl1,Sky Level 1 Altitude in feet.
skyl2,Sky Level 2 Altitude in feet.
skyl3,Sky Level 3 Altitude in feet.
skyl4,Sky Level 4 Altitude in feet.
wxcodes,Present Weather Codes (space-separated).
ice_accretion_1hr,Ice Accretion over 1 Hour (inches).
ice_accretion_3hr,Ice Accretion over 3 Hours (inches).
ice_accretion_6hr,Ice Accretion over 6 Hours (inches).
peak_wind_gust,Peak Wind Gust (from PK WND METAR remark) in knots.
peak_wind_drct,Peak Wind Gust Direction (from PK WND METAR remark) in degrees.
peak_wind_time,Peak Wind Gust Time (from PK WND METAR remark).
feel,Apparent Temperature (Wind Chill or Heat Index) in Fahrenheit.
metar,Unprocessed reported observation in METAR format.
snowdepth,Snow depth (available at select sites; units typically in inches).
"""

stations = [
    '0F2', '11R', '18H', '25T', '2F5', '2R9', '3T5', '4F2', '5C1', '5R3', '5T9', '60R', '66R', '6P9', '6R3', '6R6',
    '81R', '8T6', 'ABI', 'ACT', 'ADS', 'AFW', 'ALI', 'AMA', 'APY', 'AQO', 'ARM', 'ASL', 'ATA', 'ATT', 'AUS', 'AXH',
    'BAZ', 'BBD', 'BBF', 'BEA', 'BGD', 'BIF', 'BKD', 'BKS', 'BMQ', 'BMT', 'BPC', 'BPG', 'BPT', 'BQX', 'BRO', 'BSM',
    'BWD', 'BYY', 'CDS', 'CFD', 'CLL', 'CNW', 'COM', 'COT', 'CPT', 'CRH', 'CRP', 'CRS', 'CVB', 'CWC', 'CXO', 'CZT',
    'DAL', 'DFW', 'DHT', 'DKR', 'DLF', 'DRT', 'DTO', 'DUX', 'DWH', 'DYS', 'DZB', 'E01', 'E11', 'E38', 'E41', 'E42',
    'E57', 'EBG', 'ECU', 'EDC', 'EFD', 'ELA', 'ELP', 'EMK', 'ERV', 'ETN', 'F00', 'F05', 'F12', 'F17', 'F44', 'F46',
    'FST', 'FTN', 'FTW', 'FWS', 'GDJ', 'GDP', 'GGG', 'GKY', 'GLE', 'GLS', 'GNC', 'GOP', 'GPM', 'GRK', 'GTU', 'GUL',
    'GVT', 'GVW', 'GVX', 'GYB', 'GYF', 'GYI', 'GZN', 'HBV', 'HDO', 'HHF', 'HHV', 'HLR', 'HOU', 'HQI', 'HQZ', 'HRL',
    'HRX', 'HYI', 'IAH', 'IKG', 'ILE', 'INJ', 'INK', 'JAS', 'JCT', 'JDD', 'JSO', 'JWY', 'JXI', 'LBB', 'LBR', 'LBX',
    'LFK', 'LHB', 'LLN', 'LNC', 'LRD', 'LUD', 'LUV', 'LVJ', 'LXY', 'LZZ', 'MAF', 'MCJ', 'MDD', 'MFE', 'MIU', 'MKN',
    'MNZ', 'MRF', 'MWL', 'MZG', 'NFW', 'NGP', 'NMT', 'NOG', 'NQI', 'OCH', 'ODO', 'OPM', 'ORG', 'OSA', 'OZA', 'PEQ',
    'PEZ', 'PIL', 'PKV', 'PPA', 'PRS', 'PRX', 'PSN', 'PSX', 'PVW', 'PWG', 'PYX', 'RAS', 'RBD', 'RBO', 'RFI', 'RKP',
    'RND', 'RPE', 'RPH', 'RWV', 'RYW', 'SAT', 'SEP', 'SEQ', 'SGR', 'SHP', 'SJT', 'SKF', 'SLR', 'SNK', 'SOA', 'SPL',
    'SPS', 'SSF', 'SWW', 'T20', 'T35', 'T65', 'T69', 'T70', 'T74', 'T77', 'T78', 'T82', 'T89', 'TFP', 'TKI', 'TME',
    'TPL', 'TRL', 'TXW', 'TYR', 'UTS', 'UVA', 'VAF', 'VCT', 'VHN', 'XBP'
]

params = {
    'station': stations,
    'data': 'tmpf,mslp,sknt,skyc1,skyc2,skyc3,skyc4',
    'year1': 2024,
    'month1': 1,
    'day1': 1,
    'hour1': 0,
    'year2': 2024,
    'month2': 1,
    'day2': 1,
    'hour2': 1,
    'tz': 'America/Chicago',
    'format': 'onlycomma',
    'latlon': 'yes',
    'elev': 'yes',
    'missing': 'M',
    'trace': 'T',
    'direct': 'yes',
    'report_type': ['3', '4']
}

# Create the 'asos' folder if it doesn't exist
os.makedirs('asos', exist_ok=True)

# Generate file name based on key parameters (data type and date range)
data_type = params['data']
start_date = f"{params['year1']}-{params['month1']:02d}-{params['day1']:02d}"
end_date = f"{params['year2']}-{params['month2']:02d}-{params['day2']:02d}"
file_name = f"asos/{data_type}_{start_date}_to_{end_date}.csv"

url = 'https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py'
response = requests.get(url, params=params)
if response.status_code == 200:
    with open(file_name, 'wb') as f:
        f.write(response.content)
    print(f"Data downloaded successfully to {file_name}.")
else:
    print(f"Error: {response.status_code} - {response.text}")