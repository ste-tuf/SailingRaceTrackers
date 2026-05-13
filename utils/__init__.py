"""Utilities for sailing race data processing."""

import pandas as pd

from .extract_current_rankings import load_latest_rankings
from .sample_tracks_by_time import load_tracks_from_result, get_precomputed_sailing_stats
from .utils import reports_to_dataframe
from .process_and_archive import process_and_archive
from .gpx_utils import create_gpx_with_metadata, gpx_to_bytes, create_poi_gpx
from .polar_model import build_polar_model, calculate_efficiency


def apply_filters(df: pd.DataFrame, selected_classes: list, target_boat: str, show_target_only: bool) -> pd.DataFrame:
    """Apply filters to rankings DataFrame.
    
    Args:
        df: Rankings DataFrame
        selected_classes: List of boat classes to filter by
        target_boat: Target boat name to filter by
        show_target_only: Whether to show only target boat
    
    Returns:
        Filtered DataFrame
    """
    df_filtered = df.copy()
    if selected_classes:
        df_filtered = df_filtered[df_filtered["boatClass"].isin(selected_classes)]
    if show_target_only and target_boat:
        df_filtered = df_filtered[df_filtered["boatName"].str.contains(target_boat, case=False, na=False)]
    return df_filtered


__all__ = [
    'load_latest_rankings',
    'load_tracks_from_result',
    'reports_to_dataframe',
    'process_and_archive',
    'create_gpx_with_metadata',
    'gpx_to_bytes',
    'create_poi_gpx',
    'get_precomputed_sailing_stats',
    'apply_filters',
    'build_polar_model',
    'calculate_efficiency',
]