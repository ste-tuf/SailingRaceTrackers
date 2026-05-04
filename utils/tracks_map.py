"""Tracks map utilities - calculations for boat positions."""

from math import radians, sin, cos, sqrt, atan2


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def get_boats_to_display(df_filtered, target_boat, tracks):
    boats = df_filtered["boatName"].tolist()
    target_name = None
    for name in boats:
        if target_boat and target_boat.lower() in str(name).lower():
            target_name = name
            break

    target_lat, target_lon = 43.5, -9
    if target_name:
        target_row = df_filtered[df_filtered["boatName"] == target_name]
        if len(target_row) > 0:
            boat_id = str(target_row["boat"].iloc[0])
            full_track = tracks.get(boat_id, [])
            if full_track:
                target_lat = full_track[-1][0]
                target_lon = full_track[-1][1]

    selected_boats = []
    if target_name:
        selected_boats.append(target_name)

    remaining_boats = [b for b in boats if b != target_name]

    distances = []
    for name in remaining_boats:
        row = df_filtered[df_filtered["boatName"] == name]
        if len(row) > 0:
            boat_id = str(row["boat"].iloc[0])
            full_track = tracks.get(boat_id, [])
            if full_track:
                lat = full_track[-1][0]
                lon = full_track[-1][1]
            else:
                lat = target_lat
                lon = target_lon
            dist = haversine_distance(target_lat, target_lon, lat, lon)
            distances.append((name, dist))

    distances.sort(key=lambda x: x[1])
    closest_10 = [d[0] for d in distances[:10]]

    first_3 = remaining_boats[:3]

    selected_boats.extend(first_3)
    selected_boats.extend(closest_10)

    selected_boats = selected_boats[:13]

    return selected_boats, target_name, target_lat, target_lon