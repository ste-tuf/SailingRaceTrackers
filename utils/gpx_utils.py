"""
GPX export utilities for sailing race tracking data.

This module provides functions to export boat tracks in GPX format
compatible with navigation software like NavimetriX and QTVLM.
"""

import gpxpy
import gpxpy.gpx
from typing import Any


def create_gpx_track(
    name: str,
    track_points: list[list[float]],
    description: str = ""
) -> gpxpy.gpx.GPX:
    """
    Create a single GPX track from points.
    
    Args:
        name: Track name
        track_points: List of [lat, lon] coordinate pairs
        description: Optional track description
        
    Returns:
        GPX object with single track
    """
    gpx = gpxpy.gpx.GPX()
    gpx.name = name
    gpx.description = description
    
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_track.name = name
    gpx.tracks.append(gpx_track)
    
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    
    for point in track_points:
        lat, lon = point[0], point[1]
        gpx_point = gpxpy.gpx.GPXTrackPoint(lat, lon)
        gpx_segment.points.append(gpx_point)
    
    return gpx


def create_combined_gpx(
    tracks_dict: dict[str, list[list[float]]],
    gpx_name: str = "Race Tracks"
) -> gpxpy.gpx.GPX:
    """
    Create a combined GPX with multiple tracks.
    
    Args:
        tracks_dict: Dict of {boat_id: [[lat, lon], ...]}
        gpx_name: Name for the root GPX element
        
    Returns:
        Combined GPX object
    """
    gpx = gpxpy.gpx.GPX()
    gpx.name = gpx_name
    
    for boat_id, track_points in tracks_dict.items():
        if not track_points:
            continue
        
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_track.name = boat_id
        gpx.tracks.append(gpx_track)
        
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        
        for point in track_points:
            lat, lon = point[0], point[1]
            gpx_point = gpxpy.gpx.GPXTrackPoint(lat, lon)
            gpx_segment.points.append(gpx_point)
    
    return gpx


def create_gpx_with_metadata(
    boats_df: Any,
    tracks_dict: dict[str, list[list[float]]]
) -> gpxpy.gpx.GPX:
    """
    Create GPX with boat metadata in track descriptions.
    
    Args:
        boats_df: DataFrame with boat info (boat, boatName, overallRank, dtf, dtl, speed, classType)
        tracks_dict: Dict of {boat_id: [[lat, lon], ...]}
        
    Returns:
        GPX object with metadata
    """
    gpx = gpxpy.gpx.GPX()
    gpx.name = "Race Tracks"
    
    for _, boat in boats_df.iterrows():
        boat_id = str(boat["boat"])
        track = tracks_dict.get(boat_id, [])
        if not track:
            continue
        
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_track.name = f"{boat['boatName']}"
        gpx_track.description = (
            f"Voile: {boat['boat']} | Classement: {boat['overallRank']} | "
            f"DTF: {boat['dtf']:.1f} nm | DTL: {boat['dtl']:.1f} nm | "
            f"Vitesse: {boat['speed']:.1f} kt"
        )
        gpx.tracks.append(gpx_track)
        
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        
        for point in track:
            lat, lon = point[0], point[1]
            gpx_point = gpxpy.gpx.GPXTrackPoint(lat, lon)
            gpx_segment.points.append(gpx_point)
    
    return gpx


def gpx_to_bytes(gpx: gpxpy.gpx.GPX) -> bytes:
    """
    Convert GPX to XML bytes.
    
    Args:
        gpx: GPX object
        
    Returns:
        XML bytes
    """
    return gpx.to_xml().encode("utf-8")


def create_poi_gpx(
    boats_df: Any,
    tracks_dict: dict[str, list[list[float]]]
) -> gpxpy.gpx.GPX:
    """
    Create GPX with waypoints (POI) for latest positions only.
    Compatible with QTVLM and other navigation software.
    
    Args:
        boats_df: DataFrame with boat info
        tracks_dict: Dict of {boat_id: [[lat, lon], ...]}
        
    Returns:
        GPX object with waypoints
    """
    gpx = gpxpy.gpx.GPX()
    gpx.name = "Race POI"
    
    for _, boat in boats_df.iterrows():
        boat_id = str(boat["boat"])
        track = tracks_dict.get(boat_id, [])
        if not track:
            continue
        
        last_point = track[-1]
        lat, lon = last_point[0], last_point[1]
        
        gpx_waypoint = gpxpy.gpx.GPXWaypoint(
            lat, lon,
            name=f"{boat['boatName']}",
            description=(
                f"Voile: {boat['boat']} | Rank: {boat['overallRank']} | "
                f"DTF: {boat['dtf']:.1f} nm | DTL: {boat['dtl']:.1f} nm | "
                f"Speed: {boat['speed']:.1f} kt"
            )
        )
        gpx.waypoints.append(gpx_waypoint)
    
    return gpx