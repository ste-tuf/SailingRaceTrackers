"""Sailing stats table component."""

import streamlit as st
import pandas as pd


def _degrees_to_arrow(degrees, opposite=False):
    if degrees is None:
        return None
    if opposite:
        degrees = (degrees + 180) % 360
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8
    arrows = ["↑", "↗", "→", "↘", "↓", "↙", "←", "↖"]
    return arrows[index]


def render(df_filtered, target_boat=None):
    stats_data = []
    for _, boat_row in df_filtered.iterrows():
        dist4h = boat_row.get("dist4h")
        dist24h = boat_row.get("dist24h")
        boat_name = boat_row["boatName"]

        if target_boat and target_boat.lower() in boat_name.lower():
            boat_name = f"⭐ {boat_name}"

        stats_row = {
            "boatName": boat_name,
            "Class": boat_row["classType"],
            "TWS": round(boat_row.get("windspeed", 0) / 10.0, 1) if boat_row.get("windspeed") else None,
            "TWD": f"{_degrees_to_arrow(boat_row.get('winddir'), opposite=True)} {boat_row.get('winddir')}",
            "Heading": f"{_degrees_to_arrow(boat_row.get('heading'))} {boat_row.get('heading')}",
            "Dist 4h": dist4h,
            "Dist 24h": dist24h,
            "1h Speed": boat_row.get("speed"),
            "1h VMG": boat_row.get("vmg"),
            "4h Speed": round(dist4h / 4.0, 1) if dist4h else None,
            "4h VMG": boat_row.get("vmg4h"),
            "24h Speed": round(dist24h / 24.0, 1) if dist24h else None,
            "24h VMG": boat_row.get("vmg24h"),
        }

        stats_data.append(stats_row)

    stats_df = pd.DataFrame(stats_data)

    speed_cols = ["1h Speed", "4h Speed", "24h Speed"]
    vmg_cols = ["1h VMG", "4h VMG", "24h VMG"]
    all_numeric_cols = speed_cols + vmg_cols + ["Dist 4h", "Dist 24h", "TWS"]

    format_dict = {col: "{:.1f}" for col in all_numeric_cols}
    format_dict["TWS"] = "{:.0f}"

    display_df = stats_df[
        ["boatName", "Class", "TWS", "TWD", "Heading", "1h Speed", "1h VMG", "4h Speed", "4h VMG", "Dist 4h", "24h Speed", "24h VMG", "Dist 24h"]
    ]

    styled = display_df.style.format(format_dict, na_rep="-").background_gradient(
        cmap="RdYlGn", subset=all_numeric_cols, vmin=0
    )

    st.dataframe(
        styled,
        width="stretch",
        hide_index=True,
    )