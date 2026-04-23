"""
Streamlit app for sailing race analysis.

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from python import CurrentRankings, TrackSampler, ProcessAndArchive


st.set_page_config(page_title="Sailing Race Tracker", layout="wide")

st.title("⛵ Sailing Race Tracker")

# Sidebar controls
st.sidebar.header("Settings")

data_source = st.sidebar.radio(
    "Data Source",
    ["boats.json", "boats_result.json"]
)

config_path = "data/config.json"

# Load data
@st.cache_data
def load_rankings(path):
    return CurrentRankings().load(path)

df = load_rankings(data_source)

if df.empty:
    st.error("No data found")
    st.stop()

# Main filters
st.sidebar.subheader("Filters")

# Boat class filter
all_classes = sorted(df["boatClass"].dropna().unique().tolist())
selected_classes = st.sidebar.multiselect(
    "Boat Class",
    all_classes,
    default=all_classes[:3] if len(all_classes) > 3 else all_classes
)

# Filter dataframe
if selected_classes:
    df_filtered = df[df["boatClass"].isin(selected_classes)]
else:
    df_filtered = df

# Tab layout
tab1, tab2, tab3 = st.tabs(["🏆 Rankings", "🗺️ Tracks", "⚙️ Process"])

with tab1:
    st.subheader("Current Rankings")
    
    # Show total boats
    st.metric("Total Boats", len(df_filtered))
    
    # Highlight target boat
    target_boat = "TUF TUF"
    
    # Format for display
    display_df = df_filtered.copy()
    display_df["boatName"] = display_df["boatName"].apply(
        lambda x: f"⭐ {x}" if target_boat.lower() in str(x).lower() else x
    )
    
    # Sort by rank
    display_df = display_df.sort_values("rank")
    
    # Show table
    st.dataframe(
        display_df[["rank", "boatName", "boatClass", "speed", "vmg", "dtf", "dtl", "heading"]],
        use_container_width=True,
        hide_index=True
    )
    
    # Top gainers chart
    st.subheader("Speed vs DTF")
    fig = px.scatter(
        display_df,
        x="dtf",
        y="speed",
        color="boatClass",
        hover_name="boatName",
        size="rank",
        title="Speed vs Distance to Finish"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("GPS Tracks")
    
    # Select boats to display
    boat_names = df_filtered["boatName"].tolist()
    selected_boats = st.multiselect(
        "Select boats to display",
        boat_names,
        default=boat_names[:3] if len(boat_names) > 3 else boat_names[:1]
    )
    
    if selected_boats:
        # Load tracks
        sampler = TrackSampler()
        tracks = sampler.sample_all(data_source, interval_minutes=30)
        
        # Filter tracks - need to get boat IDs
        boat_ids = df_filtered[df_filtered["boatName"].isin(selected_boats)]["boat"].tolist()
        
        # Create map
        fig = go.Figure()
        
        colors = px.colors.qualitative.Plotly
        
        for i, boat_id in enumerate(boat_ids):
            track = tracks.get(str(boat_id), [])
            if track:
                lats = [p[0] for p in track]
                lons = [p[1] for p in track]
                name = df_filtered[df_filtered["boat"] == boat_id]["boatName"].iloc[0]
                fig.add_trace(go.Scattermapbox(
                    lat=lats,
                    lon=lons,
                    mode="lines+markers",
                    name=name,
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
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select boats to display tracks")

with tab3:
    st.subheader("Process & Archive")
    
    st.info("Process race data and create timestamped archive")
    
    if st.button("Create Archive"):
        with st.spinner("Processing..."):
            try:
                arch_path = ProcessAndArchive().run(
                    config_path=config_path,
                    boats_json_path="data/boats.json",
                    tracks_json_path="data/tracks.json",
                    output_dir="data/processed"
                )
                st.success(f"Archive created: {arch_path}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Show existing archives
    import os
    import glob
    
    st.subheader("Existing Archives")
    archives = glob.glob("data/processed/*.json")
    archives = sorted(archives, reverse=True)
    
    if archives:
        for arch in archives[:5]:
            ts = os.path.basename(arch).replace(".json", "")
            st.text(f"📁 {ts}")
    else:
        st.info("No archives yet")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Sailing Race Tracker | Python + Streamlit")