"""Sailing stats table component."""

import streamlit as st
import pandas as pd
from utils import get_precomputed_sailing_stats


def render(df_filtered, data_dir):
    precomputed_stats = get_precomputed_sailing_stats(f"{data_dir}/boats.json")

    stats_data = []
    for _, boat_row in df_filtered.iterrows():
        boat_id = str(boat_row["boat"])
        hour_stats = precomputed_stats.get(boat_id, {})

        stats_row = {
            "boatName": boat_row["boatName"],
            "Class": boat_row["classType"],
            "TWS": boat_row.get("tws"),
            "TWD": boat_row.get("twd"),
            "Dist 4h": boat_row.get("dist4h"),
            "Dist 24h": boat_row.get("dist24h"),
        }

        for hours in [1, 4, 24]:
            hs = hour_stats.get(hours, {})
            stats_row[f"{hours}h Speed"] = hs.get("speed")
            stats_row[f"{hours}h VMG"] = hs.get("vmg")

        stats_data.append(stats_row)

    stats_df = pd.DataFrame(stats_data)

    speed_cols = ["1h Speed", "4h Speed", "24h Speed"]
    vmg_cols = ["1h VMG", "4h VMG", "24h VMG"]
    all_numeric_cols = speed_cols + vmg_cols + ["Dist 4h", "Dist 24h"]

    format_dict = {col: "{:.1f}" for col in all_numeric_cols}
    format_dict["TWS"] = "{:.0f}"
    format_dict["TWD"] = "{:.0f}"

    st.dataframe(
        stats_df[
            ["boatName", "Class", "TWS", "TWD", "Dist 4h", "Dist 24h", "1h Speed", "1h VMG", "4h Speed", "4h VMG", "24h Speed", "24h VMG"]
        ].style.format(format_dict, na_rep="-").background_gradient(
            cmap="RdYlGn", subset=all_numeric_cols, vmin=0
        ),
        width="stretch",
        hide_index=True,
    )