"""Tracks tab - shows GPS tracks on a map."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def apply_filters(df, selected_classes, target_boat, show_target_only):
    df_filtered = df.copy()
    if selected_classes:
        df_filtered = df_filtered[df_filtered["boatClass"].isin(selected_classes)]
    if show_target_only and target_boat:
        df_filtered = df_filtered[df_filtered["boatName"].str.contains(target_boat, case=False, na=False)]
    return df_filtered


def render(rankings_df, selected_classes, target_boat, show_target_only, tracks):
    df_filtered = apply_filters(rankings_df, selected_classes, target_boat, show_target_only)
    
    st.subheader("GPS Tracks")

    boat_options = df_filtered["boatName"].tolist()
    selected_boats = st.multiselect(
        "Select boats to display",
        boat_options,
        default=boat_options[:3] if len(boat_options) > 3 else boat_options[:1],
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
                fig.add_trace(
                    go.Scattermapbox(
                        lat=lats,
                        lon=lons,
                        mode="lines+markers",
                        name=boat_name,
                        marker=dict(size=6, color=colors[i % len(colors)]),
                        line=dict(width=2),
                    )
                )

        fig.update_layout(
            mapbox=dict(style="open-street-map", center=dict(lat=43.5, lon=-9), zoom=5),
            margin=dict(l=0, r=0, t=30, b=0),
            height=500,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Select boats to display tracks")