"""
Shared utilities for Python sailing race analysis.
"""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def load_xml_config(path: str) -> ET.Element:
    """
    Load and parse XML configuration file.
    
    Args:
        path: Path to XML config file
        
    Returns:
        Parsed XML ElementTree root
    """
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return ET.fromstring(content)


def load_json(path: str) -> dict:
    """
    Load JSON file.
    
    Args:
        path: Path to JSON file
        
    Returns:
        Parsed JSON as dict
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Any, path: str, indent: int = 2) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        path: Output path
        indent: JSON indentation level
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)


def extract_boat_info(config_path: str) -> dict:
    """
    Extract boat information from XML configuration.
    
    Args:
        path: Path to XML config file
        
    Returns:
        Dict indexed by boat ID with boatName, skipperNames, category, boatClass
    """
    root = load_xml_config(config_path)
    boats_node = root.find('.//boats')
    if boats_node is None:
        return {}
    
    boatinfo = {}
    for boatclass in boats_node.findall('boatclass'):
        category = boatclass.get('name', '')
        for boat in boatclass.findall('boat'):
            boat_id = boat.get('id')
            if boat_id is None:
                continue
            
            crew = boat.find('crew')
            skipper_names = []
            if crew is not None:
                for navigator in crew.findall('navigator'):
                    fname = navigator.get('fname', '')
                    lname = navigator.get('lname', '')
                    if fname or lname:
                        skipper_names.append(f"{fname}_{lname}")
            
            skipper_combined = '_&_'.join(skipper_names)
            
            boatinfo[boat_id] = {
                'boatName': boat.get('name', ''),
                'skipperNames': skipper_combined,
                'category': category,
                'boatClass': boat.get('comment', '')
            }
    
    return boatinfo


def detect_figaro_class(boat_class: str, patterns: list[str] | None = None) -> bool:
    """
    Detect if a boat class matches Figaro patterns using regex.
    
    Args:
        boat_class: The boat class string (e.g., "Figaro 2", "JPK1010")
        patterns: List of regex patterns to match. Defaults to ['(?i)figaro']
        
    Returns:
        True if boat class matches any Figaro pattern
    """
    if patterns is None:
        patterns = [r'(?i)figaro']
    
    if not boat_class:
        return False
    
    for pattern in patterns:
        if re.search(pattern, boat_class):
            return True
    
    return False


# Column indices from boats.json history lines
# Based on: ["boat","racestatus","rank","progress","dtf","dtl","dtlProgress","heading","speed","vmg",...]
BOAT_COLUMNS = {
    'boat': 0,
    'racestatus': 1,
    'rank': 2,
    'progress': 3,
    'dtf': 4,
    'dtl': 5,
    'dtp': 6,
    'heading': 7,
    'speed': 8,
    'vmg': 9,
    'offset': 10,
    'heading4h': 11,
    'dist4h': 12,
    'vmg4h': 13,
    'dog4h': 14,
    'heading24h': 15,
    'dist24h': 16,
    'maxdist24h': 17,
    'vmg24h': 18,
    'dog24h': 19,
    'winddir': 29,
    'windspeed': 30,
    'windgust': 31,
}


def get_column_value(line: list, column: str) -> Any:
    """
    Get value from a boats.json history line by column name.
    
    Args:
        line: List of values from boats.json
        column: Column name from BOAT_COLUMNS
        
    Returns:
        Value at column index, or None if not found
    """
    idx = BOAT_COLUMNS.get(column)
    if idx is not None and idx < len(line):
        return line[idx]
    return None


def reports_to_dataframe(reports_path: str) -> "pd.DataFrame":
    """
    Read reports.json and convert to a pandas DataFrame.
    Each row represents a boat at a specific time point.
    
    Args:
        reports_path: Path to reports.json file
        
    Returns:
        DataFrame with columns: timestamp, snapshot_id, and all boat attributes
    """
    if not HAS_PANDAS:
        raise ImportError("pandas is required for this function")
    
    data = load_json(reports_path)
    history = data.get('reports', {}).get('history', [])
    columns = data.get('reports', {}).get('columns', [])
    
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
                else:
                    row[col] = None
            rows.append(row)
    
    return pd.DataFrame(rows)