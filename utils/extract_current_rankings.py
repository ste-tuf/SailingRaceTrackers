"""
Extract current rankings from race data.

This module loads current rankings from boats.json and provides
filtering for specific boat classes like Figaro.
"""

import pandas as pd
from pathlib import Path

from .utils import (
    BOAT_COLUMNS,
    detect_figaro_class,
    load_json,
)


def load_boats_json(boats_json_path: str) -> dict:
    """
    Load raw boats.json data.
    
    Args:
        boats_json_path: Path to boats.json file
        
    Returns:
        Parsed JSON dict
    """
    return load_json(boats_json_path)


def get_latest_timestamp(boats_json: dict) -> str | None:
    """
    Extract the latest timestamp from boats.json history.
    
    Args:
        boats_json: Parsed boats.json dict
        
    Returns:
        Latest timestamp string or None
    """
    history = boats_json.get('reports', {}).get('history', [])
    if not history:
        return None
    return history[-1].get('date')


def get_race_state(boats_json: dict) -> str:
    """
    Extract race state from boats.json.
    
    Args:
        boats_json: Parsed boats.json dict
        
    Returns:
        Race state string (e.g., 'RUNNING', 'FINISHED')
    """
    return boats_json.get('reports', {}).get('state', 'UNKNOWN')


def load_boatinfo(boatinfo_path: str | None = None) -> dict:
    """
    Load boatinfo data.
    
    Args:
        boatinfo_path: Optional path to boatinfo.json
        
    Returns:
        Boat info dict indexed by boat ID
    """
    if boatinfo_path and Path(boatinfo_path).exists():
        return load_json(boatinfo_path)
    
    default_path = "data/boatinfo.json"
    if Path(default_path).exists():
        return load_json(default_path)
    
    return {}


def load_latest_rankings(boats_json_path: str, boatinfo_path: str | None = None) -> tuple[pd.DataFrame, str, str | None]:
    """
    Load latest rankings from boats.json with all columns preserved.
    
    Loads the latest snapshot from boats.json history and joins with
    boat info to get boat names and classes. Keeps all columns from
    the raw data.
    
    Args:
        boats_json_path: Path to boats.json file
        boatinfo_path: Optional path to boatinfo.json

    Returns:
        Tuple of (DataFrame with all columns, race state, latest timestamp)
    """
    boats_json = load_json(boats_json_path)
    boatinfo = load_boatinfo(boatinfo_path)
    
    history = boats_json.get('reports', {}).get('history', [])
    if not history:
        return pd.DataFrame(), 'UNKNOWN', None
    
    latest = history[-1]
    lines = latest.get('lines', [])
    columns = boats_json.get('reports', {}).get('columns', [])
    
    if not lines:
        return pd.DataFrame(), get_race_state(boats_json), get_latest_timestamp(boats_json)
    
    records = []
    for line in lines:
        racestatus = line[BOAT_COLUMNS['racestatus']]
        if racestatus != 'RAC':
            continue
        
        boat_id = str(line[BOAT_COLUMNS['boat']])
        binfo = boatinfo.get(boat_id, {})
        
        record = {}
        for i, col in enumerate(columns):
            if i < len(line):
                record[col] = line[i]
        
        record['boatName'] = binfo.get('boatName', '')
        record['category'] = binfo.get('category', '')
        record['boatClass'] = binfo.get('boatClass', '')
        record['skipperNames'] = binfo.get('skipperNames', '')
        
        records.append(record)
    
    df = pd.DataFrame(records)
    
    return df, get_race_state(boats_json), get_latest_timestamp(boats_json)


def load_history_dataframe(boats_json_path: str) -> pd.DataFrame:
    """
    Load entire boats.json history as a DataFrame.
    
    Each row represents a boat at a specific snapshot time.
    
    Args:
        boats_json_path: Path to boats.json
        
    Returns:
        DataFrame with snapshot_id, timestamp, and all boat columns
    """
    boats_json = load_json(boats_json_path)
    
    history = boats_json.get('reports', {}).get('history', [])
    columns = boats_json.get('reports', {}).get('columns', [])
    
    rows = []
    for snapshot in history:
        snapshot_id = snapshot.get('id')
        timestamp = snapshot.get('date')
        lines = snapshot.get('lines', [])
        
        for line in lines:
            row = {
                'snapshot_id': snapshot_id,
                'timestamp': timestamp,
            }
            for i, col in enumerate(columns):
                if i < len(line):
                    row[col] = line[i]
            rows.append(row)
    
    return pd.DataFrame(rows)


def filter_by_class(
    df: pd.DataFrame,
    patterns: list[str] | None = None,
    column: str = 'boatClass'
) -> pd.DataFrame:
    """
    Filter DataFrame by boat class using regex patterns.
    
    Args:
        df: DataFrame with boat data
        patterns: List of regex patterns to match. Defaults to ['(?i)figaro']
        column: Column name to search in
        
    Returns:
        Filtered DataFrame with only matching boats
    """
    if patterns is None:
        patterns = [r'(?i)figaro']
    
    if df.empty:
        return df
    
    mask = df[column].apply(lambda x: detect_figaro_class(str(x), patterns=patterns))
    return df[mask].copy()