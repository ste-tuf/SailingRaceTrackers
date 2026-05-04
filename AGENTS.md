# SailingRaceTrackers - Agent Instructions

## Quick Start
```bash
uv sync
streamlit run app.py
```

## Key Commands
- `uv sync` - Install Python dependencies
- `streamlit run app.py` - Launch the Streamlit web application

## Project Structure
```
SailingRaceTrackers/
├── app.py              # Main entry point (thin - only orchestration)
├── components/         # UI components (st.* calls)
│   ├── sidebar.py      # Filter controls
│   ├── rankings_tab.py # Rankings display
│   ├── tracks_tab.py   # GPS tracks map
│   ├── analysis_tab.py # Charts and analysis
│   └── export_tab.py   # GPX export
├── utils/              # Business logic (pure Python, no st.*)
│   └── __init__.py     # Data loading functions
├── python/             # Core package (data processing)
│   ├── extract_current_rankings.py
│   ├── sample_tracks_by_time.py
│   ├── process_and_archive.py
│   ├── utils.py
│   └── gpx_utils.py
├── data/               # Data directory
└── pyproject.toml      # Python project configuration
```

## Architecture Principles

### 1. Keep app.py thin
- Only orchestration (load data, call components)
- No business logic

### 2. Use @st.cache_data for data loading
```python
@st.cache_data
def load_all_data():
    rankings_df, race_state, latest_timestamp = load_latest_rankings(f"{DATA_DIR}/boats.json")
    tracks = load_tracks_from_result(f"{DATA_DIR}/boats_result.json")
    reports_df = reports_to_dataframe(f"{DATA_DIR}/reports.json")
    return rankings_df, tracks, latest_timestamp, race_state, reports_df
```

### 3. Separate concerns clearly
| Folder | What goes here |
|--------|----------------|
| app.py | Entry point - only st.* calls for layout |
| components/ | Reusable UI - call st.* directly |
| utils/ | Pure Python - no st.* calls |
| python/ | Core package - data processing |

### 4. Component pattern
```python
# components/sidebar.py
import streamlit as st

def render(rankings_df, latest_timestamp, race_state):
    """Render sidebar - calls st.* directly."""
    st.sidebar.header("Settings")
    # ... controls
    return target_boat, selected_classes, show_target_only
```

### 5. Import convention
```python
# app.py
from utils import load_latest_rankings, load_tracks_from_result, reports_to_dataframe
from components import sidebar, rankings_tab, tracks_tab, analysis_tab, export_tab
```

## Important Notes
- Each race has its own branch (`prod-*`)
- Data is loaded once at startup via @st.cache_data
- Filter logic is in components, not app.py

## Dependencies
- `streamlit` - Web application framework
- `pandas`, `numpy` - Data processing
- `plotly` - Visualization
- `gpxpy` - GPX handling
- `pyproj` - Geodetic calculations