# SailingRaceTrackers - Agent Instructions

## Quick Start
```bash
uv sync
streamlit run app.py
```

## Key Commands
- `uv sync` - Install Python dependencies
- `streamlit run app.py` - Launch the Streamlit web application
- `python python/extract_current_rankings.py` - Extract rankings to JSON

## Project Structure
- `app.py` - Streamlit web application (main entry point)
- `python/` - Python package modules
- `data/` - Data directory (boats.json, tracks.json, boats_result.json)
- `pyproject.toml` - Python project configuration

## Python Modules
- `python/extract_current_rankings.py` - Current rankings extraction
- `python/sample_tracks_by_time.py` - Track sampling and stats
- `python/process_and_archive.py` - Data archiving
- `python/utils.py` - Shared utilities

## Important Notes
- Each race has its own branch (`prod-*`). The active branch appears in `.github/workflows/generate-boats-result-template.yml`
- The web app is served via Streamlit
- Data is loaded from `data/` directory

## Generated Output Format (boats_result.json)
```json
{
  "result": {
    "123": {
      "sail": 123, "rank": 1, "heading": 245, "speed": 18.5,
      "lat_dec": 46.275, "lon_dec": -1.475,
      "dtf": 1234.5, "dtl": 0.0, "dtp": 45.2,
      "track": [[lat, lon], ...]
    }
  }
}
```

## Dependencies
- `streamlit` - Web application framework
- `pandas`, `numpy` - Data processing
- `plotly` - Visualization
- `gpxpy` - GPX handling
- `pyproj` - Geodetic calculations