"""
Streamlit app for sailing race analysis.

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import glob
import os
import io
from datetime import datetime

from python import CurrentRankings, TrackSampler, ProcessAndArchive, load_json
from python import compute_all_sailing_stats, get_precomputed_sailing_stats
from python import create_gpx_with_metadata, gpx_to_bytes
from python.utils import BOAT_COLUMNS
from pyproj import CRS

# Create Geod once at module level
_CRS = CRS.from_epsg(4326)
_GEOD = _CRS.get_geod()


st.set_page_config(page_title="Sailing Race Tracker", layout="wide")

st.title("⛵ Sailing Race Tracker")

DATA_DIR = "data"

# Load all data sources at startup
@st.cache_data
def load_all_data():
    """Load all data sources and merge them."""
    # Rankings from boats.json
    df_rankings = CurrentRankings().load(f"{DATA_DIR}/boats.json")
    
    # Load full tracks directly from boats_result.json (no downsampling)
    raw_results = load_json(f"{DATA_DIR}/boats_result.json")
    tracks = {bid: data.get('track', []) for bid, data in raw_results.get('result', {}).items()}
    
    # Load raw tracks for timestamps
    raw_tracks = load_json(f"{DATA_DIR}/tracks.json")
    
    # Load boats.json once for history
    boats_json = load_json(f"{DATA_DIR}/boats.json")
    history = boats_json.get("reports", {}).get("history", [])
    latest_timestamp = history[-1].get("date") if history else None
    
    return df_rankings, tracks, raw_tracks, latest_timestamp, boats_json

df_rankings, tracks, raw_tracks, latest_timestamp, boats_json_history = load_all_data()

if df_rankings.empty:
    st.error("No data found")
    st.stop()

# Sidebar controls
st.sidebar.header("Settings")
st.sidebar.caption(f"Data: {latest_timestamp or 'unknown'}")

# Main filters
st.sidebar.subheader("Filters")

# Target boat
target_boat = "TUF TUF"
st.sidebar.text_input("Target Boat", value=target_boat, key="target_input")

# Boat class filter - using all classes from rankings
all_classes = sorted(df_rankings["boatClass"].dropna().unique().tolist())
selected_classes = st.sidebar.multiselect(
    "Boat Class",
    all_classes,
    default=[]
)

# Filter by target boat
show_target_only = st.sidebar.checkbox("Show Target Boat Only", value=False)

# Filter dataframe
df_filtered = df_rankings.copy()
if selected_classes:
    df_filtered = df_filtered[df_filtered["boatClass"].isin(selected_classes)]
if show_target_only:
    target_val = st.session_state.target_input
    df_filtered = df_filtered[df_filtered["boatName"].str.contains(target_val, case=False, na=False)]

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Rankings", "🗺️ Tracks", "📊 Analysis", "📥 Export"])

with tab1:
    st.subheader("Current Rankings")
    
    # Add class type (Duo/solo) and class-specific rank
    df_filtered = df_filtered.copy()
    df_filtered["classType"] = df_filtered["category"].apply(lambda x: "Duo" if str(x).lower() == "duo" else "Solo")
    
    # Calculate class rank by DTF (lower is better)
    df_filtered["classRank"] = df_filtered.groupby("classType")["dtf"].rank(method="min").astype(int)
    
    # Overall rank by DTF
    df_filtered["overallRank"] = df_filtered["dtf"].rank(method="min").astype(int)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Boats", len(df_filtered))
    col2.metric("Duo Boats", len(df_filtered[df_filtered["classType"] == "Duo"]))
    col3.metric("Target DTF Rank", df_filtered[df_filtered["boatName"].str.contains(target_boat, case=False, na=False)]["overallRank"].min() if len(df_filtered[df_filtered["boatName"].str.contains(target_boat, case=False, na=False)]) > 0 else "-")
    
    # Format for display
    display_df = df_filtered.copy()
    display_df["boatName"] = display_df["boatName"].apply(
        lambda x: f"⭐ {x}" if target_boat.lower() in str(x).lower() else x
    )
    
    # Sort by DTF (lower is better for racing)
    display_df = display_df.sort_values("dtf")
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        "overallRank": "Rank",
        "classType": "Class",
        "classRank": "Class Rank",
        "boatClass": "Boat Class",
        "dtf": "DTF",
        "dtl": "DTL"
    })
    
    # Show table
    st.dataframe(
        display_df[["Rank", "boatName", "Class", "Class Rank", "Boat Class", "DTF", "DTL"]],
        width='stretch',
        height=600,
        hide_index=True
    )
    
    # Sailing stats over time windows
    st.markdown("### Sailing Stats by Time Window")
    
    # Use pre-computed stats from boats.json history
    precomputed_stats = get_precomputed_sailing_stats(f"{DATA_DIR}/boats.json")
    
    # Build stats dataframe
    stats_data = []
    for bid, boat_row in df_filtered.iterrows():
        boat_id = str(boat_row["boat"])
        hour_stats = precomputed_stats.get(boat_id, {})
        
        stats_row = {
            "boatName": boat_row["boatName"],
            "Class": boat_row["classType"]
        }
        
        for hours in [1, 4, 12, 24, 48]:
            hs = hour_stats.get(hours, {})
            stats_row[f"{hours}h Speed"] = hs.get("speed")
            stats_row[f"{hours}h VMG"] = hs.get("vmg")
            stats_row[f"{hours}h TWA"] = None  # Not available in pre-computed
        
        stats_data.append(stats_row)
    
    stats_df = pd.DataFrame(stats_data)
    
    # Format for display
    speed_cols = [c for c in stats_df.columns if "Speed" in c]
    vmg_cols = [c for c in stats_df.columns if "VMG" in c]
    twa_cols = [c for c in stats_df.columns if "TWA" in c]
    all_numeric_cols = speed_cols + vmg_cols
    
    format_dict = {col: "{:.1f}" for col in all_numeric_cols}
    format_dict.update({col: "{:.0f}" for col in twa_cols})
    
    # Apply color scale
    st.dataframe(
        stats_df.style.format(format_dict, na_rep="-").background_gradient(
            cmap="RdYlGn",
            subset=all_numeric_cols,
            vmin=0
        ),
        width='stretch',
        hide_index=True
    )

with tab2:
    st.subheader("GPS Tracks")
    
    # Select boats to display
    boat_options = df_filtered["boatName"].tolist()
    selected_boats = st.multiselect(
        "Select boats to display",
        boat_options,
        default=boat_options[:3] if len(boat_options) > 3 else boat_options[:1]
    )
    
    if selected_boats:
        # Create map
        fig = go.Figure()
        
        colors = px.colors.qualitative.Plotly
        
        for i, boat_name in enumerate(selected_boats):
            boat_row = df_filtered[df_filtered["boatName"] == boat_name]
            if len(boat_row) == 0:
                continue
            boat_id = boat_row["boat"].iloc[0]
            track = tracks.get(str(boat_id), [])
            
            if track:
                lats = [p[0] for p in track]
                lons = [p[1] for p in track]
                fig.add_trace(go.Scattermapbox(
                    lat=lats,
                    lon=lons,
                    mode="lines+markers",
                    name=boat_name,
                    marker=dict(size=6, color=colors[i % len(colors)]),
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=43.5, lon=-9),
                zoom=5
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            height=500,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Select boats to display tracks")

with tab3:
    st.subheader("Race Analysis")
    
    # Speed vs DTF scatter
    fig_scatter = px.scatter(
        df_filtered,
        x="dtf",
        y="speed",
        color="boatClass",
        hover_name="boatName",
        size="rank",
        title="Speed vs Distance to Finish"
    )
    st.plotly_chart(fig_scatter, width='stretch')
    
    # Rankings over time (from history)
    st.subheader("Rank History")
    
    # Use cached history from load_all_data
    history = boats_json_history.get("reports", {}).get("history", [])
    
    if history and len(history) > 1:
        # Parse history into time series
        target_id = df_rankings[df_rankings["boatName"].str.contains(target_boat, case=False, na=False)]["boat"].iloc[0]
        
        history_data = []
        for entry in history:
            entry_date = entry.get("date", "")
            lines = entry.get("lines", [])
            for line in lines:
                if line[BOAT_COLUMNS["racestatus"]] == "RAC" and int(line[BOAT_COLUMNS["boat"]]) == target_id:
                    history_data.append({
                        "time": entry_date,
                        "rank": line[BOAT_COLUMNS["rank"]],
                        "speed": line[BOAT_COLUMNS["speed"]],
                        "dtf": line[BOAT_COLUMNS["dtf"]],
                        "dtl": line[BOAT_COLUMNS["dtl"]]
                    })
        
        if history_data:
            hist_df = pd.DataFrame(history_data)
            hist_df["time"] = pd.to_datetime(hist_df["time"])
            hist_df = hist_df.sort_values("time")
            
            # Rank over time
            fig_rank = px.line(hist_df, x="time", y="rank", markers=True, title=f"{target_boat} Rank Over Time")
            fig_rank.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_rank, width='stretch')
            
            # DTF over time
            fig_dtf = px.line(hist_df, x="time", y="dtf", markers=True, title=f"{target_boat} Distance to Finish Over Time")
            st.plotly_chart(fig_dtf, width='stretch')
    else:
        st.info("No historical data available")
    
    st.subheader("Process Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Create Archive"):
            with st.spinner("Processing..."):
                try:
                    arch_path = ProcessAndArchive().run(
                        config_path=f"{DATA_DIR}/config.json",
                        boats_json_path=f"{DATA_DIR}/boats.json",
                        tracks_json_path=f"{DATA_DIR}/tracks.json",
                        output_dir=f"{DATA_DIR}/processed"
                    )
                    st.success(f"Archive: {os.path.basename(arch_path)}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        archives = sorted(glob.glob(f"{DATA_DIR}/processed/*.json"), reverse=True)
        if archives:
            st.caption(f"Latest: {os.path.basename(archives[0])}")

with tab4:
    st.subheader("Export for Navigation Software")
    
    st.markdown("""
    Export boat tracks in GPX format (positions only) compatible with **NavimetriX**, **QTVLM**.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Duo Boats (GPX)", width='stretch'):
            try:
                duo_boats = df_filtered[df_filtered["classType"] == "Duo"]
                gpx = create_gpx_with_metadata(duo_boats, tracks)
                
                gpx_data = io.BytesIO()
                gpx_data.write(gpx_to_bytes(gpx))
                gpx_data.seek(0)
                
                st.download_button(
                    label="Download Duo Boats GPX",
                    data=gpx_data.getvalue(),
                    file_name=f"duo_boats_{datetime.now().strftime('%Y%m%d_%H%M')}.gpx",
                    mime="application/gpx+xml"
                )
                st.success(f"Exported {len(duo_boats)} Duo boats")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("Export Solo Boats (GPX)", width='stretch'):
            try:
                solo_boats = df_filtered[df_filtered["classType"] == "Solo"]
                gpx = create_gpx_with_metadata(solo_boats, tracks)
                
                gpx_data = io.BytesIO()
                gpx_data.write(gpx_to_bytes(gpx))
                gpx_data.seek(0)
                
                st.download_button(
                    label="Download Solo Boats GPX",
                    data=gpx_data.getvalue(),
                    file_name=f"solo_boats_{datetime.now().strftime('%Y%m%d_%H%M')}.gpx",
                    mime="application/gpx+xml"
                )
                st.success(f"Exported {len(solo_boats)} Solo boats")
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    
    st.subheader("Distance to Waypoint")
    
    col1, col2 = st.columns(2)
    with col1:
        wp_lat = st.number_input("Waypoint Latitude", value=0.0, format="%.5f")
    with col2:
        wp_lon = st.number_input("Waypoint Longitude", value=0.0, format="%.5f")
    
    summary_data = []
    for _, boat in df_filtered.iterrows():
        boat_id = str(boat["boat"])
        track = tracks.get(boat_id, [])
        
        if track:
            last_point = track[-1]
            lat, lon = last_point[0], last_point[1]
            
            azi, azi2, dist = _GEOD.inv(lon, lat, wp_lon, wp_lat)
            dist_nm = abs(dist) / 1852.0
            
            summary_data.append({
                "Rank": boat["overallRank"],
                "Class": boat["classType"],
                "Name": boat["boatName"],
                "Sail": boat["boat"],
                "DTF": boat["dtf"],
                "DTL": boat["dtl"],
                "Speed": boat["speed"],
                "Lat": f"{lat:.5f}",
                "Lon": f"{lon:.5f}",
                "Dist to WP": dist_nm,
            })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values("Rank")
    
    st.dataframe(
        summary_df,
        width='stretch',
        hide_index=True,
        column_config={
            "Dist to WP": st.column_config.NumberColumn(
                "Dist to WP (nm)",
                format="%.1f nm"
            )
        }
    )

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Sailing Race Tracker | Python + Streamlit")