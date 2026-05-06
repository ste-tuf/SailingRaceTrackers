"""Export tab - GPX export and waypoint distance calculations."""

import streamlit as st
import pandas as pd
import io
from datetime import datetime

from utils import create_gpx_with_metadata, gpx_to_bytes, apply_filters, create_poi_gpx


def render(rankings_df, selected_classes, target_boat, show_target_only, tracks, data_dir, geod):
    df_filtered = apply_filters(rankings_df, selected_classes, target_boat, show_target_only)
    
    df_filtered = df_filtered.copy()
    df_filtered["classType"] = df_filtered["category"].apply(
        lambda x: "Duo" if str(x).lower() == "duo" else "Solo"
    )
    df_filtered["classRank"] = (
        df_filtered.groupby("classType")["dtf"].rank(method="min").astype(int)
    )
    df_filtered["overallRank"] = df_filtered["dtf"].rank(method="min").astype(int)

    st.subheader("Export")

    duo_boats = df_filtered[df_filtered["classType"] == "Duo"]
    solo_boats = df_filtered[df_filtered["classType"] == "Solo"]

    all_boats = df_filtered[["boat", "boatName"]].drop_duplicates()
    boat_options = {f"{row['boatName']} ({row['boat']})": row['boat'] for _, row in all_boats.iterrows()}
    
    default_index = 0
    if target_boat:
        for idx, name in enumerate(list(boat_options.keys())):
            if target_boat.lower() in name.lower():
                default_index = idx
                break

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Duo Track", key="btn_duo_track", use_container_width=True):
            pass
    with col2:
        if st.button("Solo Track", key="btn_solo_track", use_container_width=True):
            pass

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Duo POI", key="btn_duo_poi", use_container_width=True):
            pass
    with col2:
        if st.button("Solo POI", key="btn_solo_poi", use_container_width=True):
            pass

    col1, col2 = st.columns(2)

    with col1:
        selected_boat = st.selectbox(
            "Select Boat", 
            options=list(boat_options.keys()),
            index=default_index,
            key="selected_boat_export"
        )
        selected_boat_sail = boat_options[selected_boat]
    with col2:
        if st.button("Export Single Track", key="btn_single_track", use_container_width=True):
            pass

    export_type = None
    gpx_data = None
    filename = None

    if st.session_state.get("btn_single_track"):
        export_type = "Single Track"
        single_boat = df_filtered[df_filtered["boat"] == selected_boat_sail]
        gpx = create_gpx_with_metadata(single_boat, tracks)
        gpx_data = io.BytesIO(gpx_to_bytes(gpx))
        filename = f"track_{selected_boat_sail}_{datetime.now().strftime('%Y%m%d_%H%M')}.gpx"
    elif st.session_state.get("btn_duo_track"):
        export_type = "Duo Track"
        gpx = create_gpx_with_metadata(duo_boats, tracks)
        gpx_data = io.BytesIO(gpx_to_bytes(gpx))
        filename = f"duo_track_{datetime.now().strftime('%Y%m%d_%H%M')}.gpx"
    elif st.session_state.get("btn_solo_track"):
        export_type = "Solo Track"
        gpx = create_gpx_with_metadata(solo_boats, tracks)
        gpx_data = io.BytesIO(gpx_to_bytes(gpx))
        filename = f"solo_track_{datetime.now().strftime('%Y%m%d_%H%M')}.gpx"
    elif st.session_state.get("btn_duo_poi"):
        export_type = "Duo POI"
        gpx = create_poi_gpx(duo_boats, tracks)
        gpx_data = io.BytesIO(gpx_to_bytes(gpx))
        filename = f"duo_poi_{datetime.now().strftime('%Y%m%d_%H%M')}.gpx"
    elif st.session_state.get("btn_solo_poi"):
        export_type = "Solo POI"
        gpx = create_poi_gpx(solo_boats, tracks)
        gpx_data = io.BytesIO(gpx_to_bytes(gpx))
        filename = f"solo_poi_{datetime.now().strftime('%Y%m%d_%H%M')}.gpx"

    if gpx_data and filename:
        st.download_button(
            label=f"Download {export_type}",
            data=gpx_data.getvalue(),
            file_name=filename,
            mime="application/gpx+xml",
            use_container_width=True,
        )

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

            azi, azi2, dist = geod.inv(lon, lat, wp_lon, wp_lat)
            dist_nm = abs(dist) / 1852.0

            summary_data.append(
                {
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
                }
            )

    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values("Rank")

    st.dataframe(
        summary_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Dist to WP": st.column_config.NumberColumn(
                "Dist to WP (nm)", format="%.1f nm"
            )
        },
    )