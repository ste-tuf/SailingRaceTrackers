"""Export tab - GPX export and waypoint distance calculations."""

import streamlit as st
import pandas as pd
import io
from datetime import datetime

from utils import create_gpx_with_metadata, gpx_to_bytes


def apply_filters(df, selected_classes, target_boat, show_target_only):
    df_filtered = df.copy()
    if selected_classes:
        df_filtered = df_filtered[df_filtered["boatClass"].isin(selected_classes)]
    if show_target_only and target_boat:
        df_filtered = df_filtered[df_filtered["boatName"].str.contains(target_boat, case=False, na=False)]
    df_filtered = df_filtered.copy()
    df_filtered["classType"] = df_filtered["category"].apply(
        lambda x: "Duo" if str(x).lower() == "duo" else "Solo"
    )
    df_filtered["classRank"] = (
        df_filtered.groupby("classType")["dtf"].rank(method="min").astype(int)
    )
    df_filtered["overallRank"] = df_filtered["dtf"].rank(method="min").astype(int)
    return df_filtered


def render(rankings_df, selected_classes, target_boat, show_target_only, tracks, data_dir, geod):
    df_filtered = apply_filters(rankings_df, selected_classes, target_boat, show_target_only)
    
    st.subheader("Export for Navigation Software")

    st.markdown("""
Export boat tracks in GPX format (positions only) compatible with **NavimetriX**, **QTVLM**.
""")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export Duo Boats (GPX)", width="stretch"):
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
                    mime="application/gpx+xml",
                )
                st.success(f"Exported {len(duo_boats)} Duo boats")
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        if st.button("Export Solo Boats (GPX)", width="stretch"):
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
                    mime="application/gpx+xml",
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