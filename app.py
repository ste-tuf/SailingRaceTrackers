"""
Sailing Race Tracker - Main entry point.

Run with: streamlit run app.py
"""

import streamlit as st
from pyproj import CRS

from utils import load_latest_rankings, load_tracks_from_result, reports_to_dataframe
from components import sidebar, rankings_tab, tracks_tab, analysis_tab, export_tab

_CRS = CRS.from_epsg(4326)
_GEOD = _CRS.get_geod()

st.set_page_config(page_title="Sailing Race Tracker", layout="wide")
st.title("⛵ Sailing Race Tracker")

DATA_DIR = "data"


@st.cache_data
def load_all_data():
    """Load all data sources once."""
    rankings_df, race_state, latest_timestamp = load_latest_rankings(f"{DATA_DIR}/boats.json")
    tracks = load_tracks_from_result(f"{DATA_DIR}/boats_result.json")
    reports_df = reports_to_dataframe(f"{DATA_DIR}/reports.json")
    return rankings_df, tracks, latest_timestamp, race_state, reports_df


rankings_df, tracks, latest_timestamp, race_state, reports_df = load_all_data()

if rankings_df.empty:
    st.error("No data found")
    st.stop()

target_boat, selected_classes, show_target_only = sidebar.render(rankings_df, latest_timestamp, race_state)

map_style = st.session_state.get("map_style", "open-street-map")

tab1, tab2, tab3, tab4 = st.tabs(["🏆 Rankings", "🗺️ Tracks", "📊 Analysis", "📥 Export"])

with tab1:
    rankings_tab.render(rankings_df, selected_classes, target_boat, show_target_only)

with tab2:
    tracks_tab.render(rankings_df, selected_classes, target_boat, show_target_only, tracks, map_style)

with tab3:
    analysis_tab.render(rankings_df, selected_classes, target_boat, show_target_only, reports_df, DATA_DIR)

with tab4:
    export_tab.render(rankings_df, selected_classes, target_boat, show_target_only, tracks, DATA_DIR, _GEOD)