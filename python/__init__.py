"""
SailingRaceTrackers Python Package

Tools for processing and analyzing sailing race tracking data.

Modules:
- process_and_archive: Process race data and create timestamped archives
- extract_current_rankings: Extract and filter current rankings
- sample_tracks_by_time: Sample GPS tracks over time intervals
- utils: Shared utilities for XML/JSON handling
- gpx_utils: GPX export utilities
"""

from .process_and_archive import ProcessAndArchive, process_and_archive
from .extract_current_rankings import (
    CurrentRankings,
    extract_current_rankings,
    get_figaro_rankings,
    filter_by_class
)
from .sample_tracks_by_time import TrackSampler, sample_track_at_interval, compute_sailing_stats, compute_all_sailing_stats, get_precomputed_sailing_stats
from .utils import (
    detect_figaro_class,
    extract_boat_info,
    load_json,
    load_xml_config,
    save_json,
    BOAT_COLUMNS,
    reports_to_dataframe,
)
from .gpx_utils import (
    create_gpx_track,
    create_combined_gpx,
    create_gpx_with_metadata,
    gpx_to_bytes,
)

__all__ = [
    # Process and archive
    'ProcessAndArchive',
    'process_and_archive',
    # Current rankings
    'CurrentRankings',
    'extract_current_rankings',
    'get_figaro_rankings',
    'filter_by_class',
    # Track sampling
    'TrackSampler',
    'sample_track_at_interval',
    # Utils
    'detect_figaro_class',
    'extract_boat_info',
    'load_json',
    'load_xml_config',
    'save_json',
    'BOAT_COLUMNS',
    'reports_to_dataframe',
    # GPX utils
    'create_gpx_track',
    'create_combined_gpx',
    'create_gpx_with_metadata',
    'gpx_to_bytes',
]