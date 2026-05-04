"""
Process race data and archive with timestamp.

This module processes boats.json (rankings), tracks.json (GPS tracks),
and config.json (boat info) to create a unified archive with timestamp.
"""

import os
from datetime import datetime
from pathlib import Path

from .utils import (
    BOAT_COLUMNS,
    detect_figaro_class,
    extract_boat_info,
    load_json,
    load_xml_config,
    save_json,
)


def find_track_by_id(tracks_data: dict, boat_id: int) -> list | None:
    """
    Find track data for a specific boat ID.
    
    Args:
        tracks_data: Parsed tracks.json dict
        boat_id: Boat ID to find
        
    Returns:
        Track list [{'id': int, 'loc': [[ts, lat, lon, dtf], ...]}, ...] or None
    """
    for track in tracks_data.get('tracks', []):
        if track.get('id') == boat_id:
            return track.get('loc')
    return None


def transform_track(loc: list) -> list[list]:
    """
    Transform raw track coordinates to GPS lat/lon.
    
    The raw track uses cumulative offsets that need to be converted:
    - Each point is [timestamp_delta, lat_offset, lon_offset, dtf]
    - lat = (lat_offset / 100000) + previous_lat
    - lon = (lon_offset / 100000) + previous_lon
    
    Args:
        loc: Raw location data from tracks.json
        
    Returns:
        List of [lat, lon] coordinate pairs
    """
    if not loc or len(loc) == 0:
        return []
    
    track = []
    first_point = loc[0]
    track.append([
        first_point[1] / 100000,
        first_point[2] / 100000
    ])
    
    for j in range(len(loc) - 1):
        prev_lat = track[j][0]
        prev_lon = track[j][1]
        new_lat = (loc[j + 1][1] / 100000) + prev_lat
        new_lon = (loc[j + 1][2] / 100000) + prev_lon
        track.append([new_lat, new_lon])
    
    return track


def process_and_archive(
    config_path: str,
    boats_json_path: str,
    tracks_json_path: str,
    output_dir: str
) -> str:
    """
    Process race data and create timestamped archive.
    
    Reads boats.json (rankings history), tracks.json (GPS tracks),
    and config.xml (boat info), merges them, and saves to timestamped archive.
    
    Args:
        config_path: Path to XML config file
        boats_json_path: Path to boats.json file
        tracks_json_path: Path to tracks.json file
        output_dir: Output directory for archived file
        
    Returns:
        Path to created archive file
    """
    boats_json = load_json(boats_json_path)
    tracks_json = load_json(tracks_json_path)
    boatinfo = extract_boat_info(config_path)
    
    history = boats_json.get('reports', {}).get('history', [])
    if not history:
        raise ValueError("No history data found in boats.json")
    
    latest = history[-1]
    lines = latest.get('lines', [])
    if not lines:
        raise ValueError("No lines data in latest history entry")
    
    result = {}
    timestamp = latest.get('date', datetime.utcnow().isoformat())
    
    for line in lines:
        racestatus = line[BOAT_COLUMNS['racestatus']]
        if racestatus != 'RAC':
            continue
        
        boat_id = int(line[BOAT_COLUMNS['boat']])
        
        track_data = find_track_by_id(tracks_json, boat_id)
        track = transform_track(track_data) if track_data else []
        
        binfo = boatinfo.get(str(boat_id), {})
        
        result[str(boat_id)] = {
            'boatName': binfo.get('boatName', ''),
            'skipperNames': binfo.get('skipperNames', ''),
            'category': binfo.get('category', ''),
            'boatClass': binfo.get('boatClass', ''),
            'rank': line[BOAT_COLUMNS['rank']],
            'speed': line[BOAT_COLUMNS['speed']],
            'vmg': line[BOAT_COLUMNS['vmg']],
            'heading': line[BOAT_COLUMNS['heading']],
            'dtf': line[BOAT_COLUMNS['dtf']],
            'dtl': line[BOAT_COLUMNS['dtl']],
            'dist4h': line[BOAT_COLUMNS['dist4h']],
            'dist24h': line[BOAT_COLUMNS['dist24h']],
            'track': track,
            'timestamp': timestamp
        }
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(output_dir, f'{ts_str}.json')
    
    save_json({'result': result, 'timestamp': timestamp}, output_path)
    
    return output_path