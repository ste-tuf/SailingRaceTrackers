"""
Sample tracks over specified time intervals.

This module provides functions to sample GPS tracks at specified intervals,
useful for reducing data size or analyzing track segments over time.
"""

import json
import math
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .utils import (
    detect_figaro_class,
    extract_boat_info,
    load_json,
)


def parse_timestamp(ts_str: str) -> datetime:
    """
    Parse ISO timestamp string to datetime.
    
    Args:
        ts_str: ISO format timestamp (e.g., "2026-04-23T15:00:00Z")
        
    Returns:
        datetime object
    """
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1] + '+00:00'
    return datetime.fromisoformat(ts_str.replace('+00:00', ''))


def compute_sailing_stats(
    track: list,
    hours_back: float,
    wind_dir: float = 0.0
) -> dict:
    """
    Compute sailing stats for a track segment over specified hours back.
    
    Args:
        track: List of [time_delta, lat_offset, lon_offset] from tracks.json
               OR List of [lat, lon] from boats_result.json
        hours_back: Hours to look back from most recent point
        wind_dir: Wind direction in degrees
        
    Returns:
        Dict with speed, vmg, tws, twa
    """
    import math
    
    if not track or len(track) < 2:
        return {"speed": None, "vmg": None, "tws": None, "twa": None}
    
    # Check track format
    first = track[0]
    if isinstance(first, int):
        return {"speed": None, "vmg": None, "tws": None, "twa": None}
    
    if len(first) == 2:
        # boats_result.json format: [lat, lon] cumulative in degrees
        # Need to use tracks.json for time data
        return {"speed": None, "vmg": None, "tws": None, "twa": None}
    
    if len(track[0]) < 3:
        return {"speed": None, "vmg": None, "tws": None, "twa": None}
    
    # tracks.json format: [time_delta, lat_offset, lon_offset]
    # First entry: [unix_timestamp, lat_offset, lon_offset]
    # Subsequent: [time_delta, lat_offset, lon_offset] (deltas - changes from prev)
    
    base_ts = track[0][0]
    
    # Build timestamps and cumulative positions
    timestamps = []
    cum_time = 0
    lats = []
    lons = []
    
    if base_ts > 1000000000:
        # First entry is Unix timestamp + lat/lon from origin
        base_lat = track[0][1] / 100000.0
        base_lon = track[0][2] / 100000.0
        timestamps.append(base_ts)
        lats.append(base_lat)
        lons.append(base_lon)
        
        # Subsequent: accumulate deltas
        for p in track[1:]:
            cum_time += p[0]
            timestamps.append(cum_time + base_ts)
            lats.append(lats[-1] + p[1] / 100000.0)
            lons.append(lons[-1] + p[2] / 100000.0)
    else:
        # All deltas
        for p in track:
            cum_time += p[0]
            timestamps.append(cum_time)
            lats.append(p[1] / 100000.0)
            lons.append(p[2] / 100000.0)
    
    now_timestamp = timestamps[-1]
    cutoff_timestamp = now_timestamp - (hours_back * 3600)
    
    segment_indices = [i for i, ts in enumerate(timestamps) if ts >= cutoff_timestamp]
    if len(segment_indices) < 2:
        start_idx = max(0, len(track) - 50)
        segment_indices = list(range(start_idx, len(track)))
    
    total_distance = 0.0
    total_time = 0.0
    
    for i in range(1, len(segment_indices)):
        idx_prev = segment_indices[i - 1]
        idx_curr = segment_indices[i]
        dt = timestamps[idx_curr] - timestamps[idx_prev]
        if dt <= 0:
            continue
        
        dlat = lats[idx_curr] - lats[idx_prev]
        dlon = lons[idx_curr] - lons[idx_prev]
        dist_deg = math.sqrt(dlat**2 + dlon**2)
        dist_km = dist_deg * 111.0
        dist_meters = dist_km * 1000
        
        total_distance += dist_meters
        total_time += dt
    
    if total_time <= 0:
        return {"speed": None, "vmg": None, "tws": None, "twa": None}
    
    avg_speed_ms = total_distance / total_time
    avg_speed_knots = avg_speed_ms * 1.94384
    
    start_idx = segment_indices[0]
    end_idx = segment_indices[-1]
    
    dlat_total = lats[end_idx] - lats[start_idx]
    dlon_total = lons[end_idx] - lons[start_idx]
    
    if abs(dlat_total) < 0.0001 and abs(dlon_total) < 0.0001:
        return {"speed": round(avg_speed_knots, 1), "vmg": round(avg_speed_knots, 1), "tws": None, "twa": 0}
    
    course = math.atan2(dlon_total, dlat_total)
    course_deg = math.degrees(course)
    twa = (course_deg - wind_dir + 360) % 360
    if twa > 180:
        twa = 360 - twa
    
    vmg = avg_speed_knots * abs(math.cos(math.radians(twa)))
    
    return {
        "speed": round(avg_speed_knots, 1),
        "vmg": round(vmg, 1),
        "tws": None,
        "twa": round(twa, 0)
    }


def compute_all_sailing_stats(
    tracks_dict: dict,
    hours_windows: list[float] = [1, 4, 12, 24, 48],
    wind_dir: float = 0.0
) -> dict:
    """
    Compute sailing stats for all boats over multiple time windows.
    
    Args:
        tracks_dict: Dict of {boat_id: track}
        hours_windows: List of hours to compute stats for
        wind_dir: Wind direction
        
    Returns:
        Dict of {boat_id: {1: {...}, 4: {...}, ...}}
    """
    result = {}
    
    for boat_id, track in tracks_dict.items():
        result[boat_id] = {}
        for hours in hours_windows:
            result[boat_id][hours] = compute_sailing_stats(track, hours, wind_dir)
    
    return result


def sample_track_at_interval(
    track: list,
    hours_back: float | None = None,
    interval_minutes: int = 30
) -> list[list[float]]:
    """
    Sample a single boat's track at specified time interval.
    
    Args:
        track: List of [lat, lon] coordinates
        hours_back: Optional hours back from now to sample from
        interval_minutes: Interval in minutes between samples
        
    Returns:
        List of [lat, lon, timestamp] sampled points
    """
    if not track or len(track) == 0:
        return []
    
    # For now, return simple sample - evenly distributed points
    # More sophisticated timestamp-based sampling can be added
    n_points = len(track)
    step = max(1, n_points // (hours_back * 60 / interval_minutes) if hours_back else n_points // 10)
    
    sampled = []
    for i in range(0, n_points, step):
        sampled.append(track[i])
    
    # Always include last point
    if track[-1] not in sampled:
        sampled.append(track[-1])
    
    return sampled


def sample_tracks_at_interval(
    tracks_dict: dict,
    hours_back: float | None = None,
    interval_minutes: int = 30
) -> dict[str, list]:
    """
    Sample multiple boat tracks at specified interval.
    
    Args:
        tracks_dict: Dict of {boat_id: [[lat, lon], ...]}
        hours_back: Hours back from current time to sample
        interval_minutes: Sample interval in minutes
        
    Returns:
        Dict of sampled tracks
    """
    result = {}
    
    for boat_id, track in tracks_dict.items():
        sampled = sample_track_at_interval(track, hours_back, interval_minutes)
        if sampled:
            result[str(boat_id)] = sampled
    
    return result


def load_tracks_from_result(path: str) -> dict[str, list]:
    """
    Load tracks from boats_result.json.
    
    Args:
        path: Path to boats_result.json
        
    Returns:
        Dict of {boat_id: [[lat, lon], ...]}
    """
    data = load_json(path)
    result = data.get('result', {})
    
    tracks = {}
    for boat_id, boat_data in result.items():
        track = boat_data.get('track', [])
        if track and len(track) > 0:
            tracks[boat_id] = track
    
    return tracks


def filter_by_class(
    data: dict,
    patterns: list[str] | None = None,
    boat_class_key: str = 'boatClass'
) -> dict:
    """
    Filter boats by class using regex patterns.
    
    Args:
        data: Dict of boat data with 'boatClass' field
        patterns: List of regex patterns (default: ['(?i)figaro'])
        boat_class_key: Key containing boat class
        
    Returns:
        Filtered dict with only matching boats
    """
    if patterns is None:
        patterns = [r'(?i)figaro']
    
    result = {}
    for boat_id, boat_data in data.items():
        boat_class = str(boat_data.get(boat_class_key, ''))
        if detect_figaro_class(boat_class, patterns=patterns):
            result[boat_id] = boat_data
    
    return result


class TrackSampler:
    """
    Sample GPS tracks over specified time intervals.
    
    Usage:
        # Sample all tracks from last 4 hours at 30-min intervals
        tracks = TrackSampler().sample_all(
            "data/boats_result.json",
            hours_back=4,
            interval_minutes=30
        )
        
        # Sample only Figaro boats
        figaro_tracks = TrackSampler().sample_by_class(
            "data/boats_result.json",
            patterns=[r'(?i)figaro'],
            hours_back=24,
            interval_minutes=60
        )
    """
    
    def sample_all(
        self,
        boats_result_json_path: str,
        hours_back: float | None = None,
        interval_minutes: int = 30
    ) -> dict[str, list]:
        """
        Sample all boat tracks.
        
        Args:
            boats_result_json_path: Path to boats_result.json
            hours_back: Optional hours to sample from
            interval_minutes: Sample interval in minutes
            
        Returns:
            Dict of {boat_id: sampled_track}
        """
        tracks = load_tracks_from_result(boats_result_json_path)
        return sample_tracks_at_interval(tracks, hours_back, interval_minutes)
    
    def sample_by_class(
        self,
        boats_result_json_path: str,
        patterns: list[str] | None = None,
        hours_back: float | None = None,
        interval_minutes: int = 30,
        class_key: str = 'boatClass',
        config_path: str | None = None
    ) -> dict[str, list]:
        """
        Sample tracks filtered by boat class.
        
        Args:
            boats_result_json_path: Path to boats_result.json
            patterns: Regex patterns for class detection
            hours_back: Optional hours back from now to sample from
            interval_minutes: Sample interval in minutes
            class_key: Key containing boat class in data (if available)
            config_path: Path to config.xml for boat class lookup
            
        Returns:
            Dict of filtered and sampled tracks
        """
        data = load_json(boats_result_json_path)
        
        # Get boat class info from config if provided
        boat_class_map = {}
        if config_path:
            boatinfo = extract_boat_info(config_path)
            for bid, info in boatinfo.items():
                boat_class_map[bid] = info.get('boatClass', '')
        
        # Filter boats
        filtered = {}
        for boat_id, boat_data in data.get('result', {}).items():
            # Get boat class from config or data
            boat_class = boat_class_map.get(boat_id, boat_data.get(class_key, ''))
            if detect_figaro_class(str(boat_class), patterns=patterns if patterns else [r'(?i)figaro']):
                filtered[boat_id] = boat_data
        
        tracks = {}
        for boat_id, boat_data in filtered.items():
            track = boat_data.get('track', [])
            if track and len(track) > 0:
                tracks[boat_id] = track
        
        return sample_tracks_at_interval(tracks, hours_back, interval_minutes)
    
    def sample_one(
        self,
        track: list,
        hours_back: float | None = None,
        interval_minutes: int = 30
    ) -> list:
        """
        Sample a single track.
        
        Args:
            track: List of [lat, lon] coordinates
            hours_back: Optional hours back to sample from
            interval_minutes: Sample interval in minutes
            
        Returns:
            Sampled track as list
        """
        return sample_track_at_interval(track, hours_back, interval_minutes)
    
    def get_figaro_tracks(
        self,
        boats_result_json_path: str,
        hours_back: float | None = None,
        interval_minutes: int = 30,
        config_path: str | None = None
    ) -> dict[str, list]:
        """
        Get sampled Figaro boat tracks.
        
        Convenience method using default Figaro patterns.
        
        Args:
            boats_result_json_path: Path to boats_result.json
            hours_back: Optional hours back
            interval_minutes: Sample interval
            config_path: Path to config.xml for boat class lookup
            
        Returns:
            Dict of Figaro tracks
        """
        return self.sample_by_class(
            boats_result_json_path,
            patterns=[r'(?i)figaro'],
            hours_back=hours_back,
            interval_minutes=interval_minutes,
            config_path=config_path
        )