"""Tracks tab - shows GPS tracks on a map."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils import apply_filters
from utils.tracks_map import get_boats_to_display


def render(rankings_df, selected_classes, target_boat, show_target_only, tracks, map_style="open-street-map"):
    df_filtered = apply_filters(
        rankings_df, selected_classes, target_boat, show_target_only
    )

    st.subheader("GPS Tracks")

    selected_boats, target_name, target_lat, target_lon = get_boats_to_display(
        df_filtered, target_boat, tracks
    )

    if selected_boats:
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
                is_target = boat_name == target_name
                
                fig.add_trace(
                    go.Scattermapbox(
                        lat=lats,
                        lon=lons,
                        mode="lines" if len(track) > 1 else "markers",
                        name=boat_name,
                        marker=dict(size=6, color=colors[i % len(colors)]),
                        line=dict(width=2),
                    )
                )
                
                last_lat = track[-1][0]
                last_lon = track[-1][1]
                fig.add_trace(
                    go.Scattermapbox(
                        lat=[last_lat],
                        lon=[last_lon],
                        mode="markers",
                        name=f"{boat_name} (end)",
                        marker=dict(size=14 if is_target else 8, color=colors[i % len(colors)]),
                        showlegend=False,
                    )
                )

        fig.update_layout(
            mapbox=dict(style=map_style, center=dict(lat=target_lat, lon=target_lon), zoom=4),
            margin=dict(l=0, r=0, t=30, b=0),
            height=800,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No boats available")