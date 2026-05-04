"""
Extract current rankings from race data.

This module loads current rankings from boats.json or archived files
and provides filtering for specific boat classes like Figaro.
"""

import pandas as pd
from pathlib import Path

from .utils import (
    BOAT_COLUMNS,
    detect_figaro_class,
    extract_boat_info,
    load_json,
)


def extract_current_rankings(
    boats_json_path: str | dict | None = None,
    boatinfo_path: str | None = None
) -> pd.DataFrame:
    """
    Extract current rankings from boats.json.
    
    Loads the latest snapshot from boats.json history and joins with
    boat info from config.xml to get boat names and classes.
    
    Args:
        boats_json_path: Path to boats.json file, or already-loaded dict
        boatinfo_path: Optional path to boatinfo.json (if already generated)

    Returns:
        DataFrame with columns: boat, rank, speed, vmg, dtf, dtl, heading,
               boatName, category, boatClass, skipperNames
    """
    if isinstance(boats_json_path, dict):
        boats_json = boats_json_path
    else:
        boats_json = load_json(boats_json_path)
    
    # Load boat info
    if boatinfo_path and Path(boatinfo_path).exists():
        boatinfo = load_json(boatinfo_path)
    else:
        default_path = "data/boatinfo.json"
        if Path(default_path).exists():
            boatinfo = load_json(default_path)
        else:
            boatinfo = {}
    
    # Get latest history entry
    history = boats_json.get('reports', {}).get('history', [])
    if not history:
        return pd.DataFrame()
    
    latest = history[-1]
    lines = latest.get('lines', [])
    if not lines:
        return pd.DataFrame()
    
    # Parse lines into records
    records = []
    for line in lines:
        racestatus = line[BOAT_COLUMNS['racestatus']]
        if racestatus != 'RAC':
            continue
        
        boat_id = str(line[BOAT_COLUMNS['boat']])
        binfo = boatinfo.get(boat_id, {})
        
        records.append({
            'boat': int(boat_id),
            'rank': line[BOAT_COLUMNS['rank']],
            'speed': line[BOAT_COLUMNS['speed']],
            'vmg': line[BOAT_COLUMNS['vmg']],
            'dtf': line[BOAT_COLUMNS['dtf']],
            'dtl': line[BOAT_COLUMNS['dtl']],
            'heading': line[BOAT_COLUMNS['heading']],
            'dist4h': line[BOAT_COLUMNS['dist4h']],
            'dist24h': line[BOAT_COLUMNS['dist24h']],
            'tws': line[BOAT_COLUMNS['windspeed']],
            'twd': line[BOAT_COLUMNS['winddir']],
            'boatName': binfo.get('boatName', ''),
            'category': binfo.get('category', ''),
            'boatClass': binfo.get('boatClass', ''),
            'skipperNames': binfo.get('skipperNames', '')
        })
    
    history = boats_json.get('reports', {}).get('history', [])
    latest_timestamp = history[-1].get('date') if history else None
    race_state = boats_json.get('reports', {}).get('state', 'UNKNOWN')
    
    return pd.DataFrame(records), race_state, latest_timestamp


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


def get_figaro_rankings(
    boats_json_path: str,
    boatinfo_path: str | None = None,
    patterns: list[str] | None = None
) -> pd.DataFrame:
    """
    Get current Figaro class rankings.
    
    Convenience function that loads rankings and filters for Figaro class.
    
    Args:
        boats_json_path: Path to boats.json file
        boatinfo_path: Optional path to boatinfo.json
        patterns: Regex patterns for Figaro detection
        
    Returns:
        DataFrame with Figaro boats sorted by rank
    """
    df = extract_current_rankings(boats_json_path, boatinfo_path)
    if df.empty:
        return df
    
    figaro_df = filter_by_class(df, patterns=patterns)
    return figaro_df.sort_values('rank').reset_index(drop=True)


class CurrentRankings:
    """
    Extract current race rankings.
    
    Usage:
        df = CurrentRankings().load("data/boats.json")
        figaro = df[df["boatClass"].str.contains("Figaro", case=False)]
    """
    
    def load(
        self,
        boats_json_path: str | dict = "data/boats.json",
        boatinfo_path: str | None = None
    ) -> tuple[pd.DataFrame, str, str | None]:
        """
        Load current rankings.

        Args:
            boats_json_path: Path to boats.json, or already-loaded dict
            boatinfo_path: Optional path to boatinfo.json

        Returns:
            Tuple of (DataFrame, race state, latest timestamp)
        """
        return extract_current_rankings(boats_json_path, boatinfo_path)
    
    def filter_figaro(
        self,
        df: pd.DataFrame,
        patterns: list[str] | None = None
    ) -> pd.DataFrame:
        """
        Filter for Figaro class boats.
        
        Args:
            df: DataFrame with rankings
            patterns: Regex patterns for detection
            
        Returns:
            Filtered DataFrame
        """
        return filter_by_class(df, patterns=patterns)
    
    def get_figaro(
        self,
        boats_json_path: str = "data/boats.json",
        boatinfo_path: str | None = None,
        patterns: list[str] | None = None
    ) -> pd.DataFrame:
        """
        Get Figaro rankings directly.
        
        Args:
            boats_json_path: Path to boats.json
            boatinfo_path: Optional path to boatinfo.json
            patterns: Regex patterns for detection
            
        Returns:
            DataFrame with Figaro boats sorted by rank
        """
        return get_figaro_rankings(boats_json_path, boatinfo_path, patterns)