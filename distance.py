import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees) using the
    Haversine formula.

    Args:
        lat1, lon1: Latitude and longitude of point 1 (in degrees).
        lat2, lon2: Latitude and longitude of point 2 (in degrees).

    Returns:
        Distance in kilometers.
    """
    # Radius of Earth in kilometers
    R = 6371.0

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


def find_closest_point(points, target_lat, target_lon):
    """
    Find the closest point from a list of (lat, lon) coordinates to a target point.

    Args:
        points: List of tuples [(lat1, lon1), (lat2, lon2), ...].
        target_lat: Latitude of the target point (in degrees).
        target_lon: Longitude of the target point (in degrees).

    Returns:
        Tuple (lat, lon) of the closest point.
    """
    if not points:
        raise ValueError("Points list cannot be empty.")

    min_distance = float('inf')
    closest_point = None

    for point in points:
        lat, lon = point
        distance = haversine_distance(target_lat, target_lon, lat, lon)

        if distance < min_distance:
            min_distance = distance
            closest_point = (lat, lon)

    return closest_point, min_distance  # Also return the distance for reference

# Example usage:
# points = [(37.7749, -122.4194), (34.0522, -118.2437), (40.7128, -74.0060)]  # SF, LA, NYC
# target = (37.7749, -122.4194)  # Target is SF
# closest, dist = find_closest_point(points, *target)
# print(f"Closest point: {closest}, Distance: {dist:.2f} km")
