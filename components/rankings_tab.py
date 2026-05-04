"""Rankings tab - shows current rankings and sailing stats."""

import streamlit as st
import pandas as pd

from utils import apply_filters
from utils.rankings_table import render as render_rankings_table
from utils.sailing_stats_table import render as render_sailing_stats_table


def render(rankings_df, selected_classes, target_boat, show_target_only):
    """Render the rankings tab."""
    df_filtered = apply_filters(rankings_df, selected_classes, target_boat, show_target_only)
    
    df_filtered = df_filtered.copy()
    df_filtered["classType"] = df_filtered["category"].apply(
        lambda x: "Duo" if str(x).lower() == "duo" else "Solo"
    )
    df_filtered["classRank"] = (
        df_filtered.groupby("classType")["dtf"].rank(method="min").astype(int)
    )
    df_filtered["overallRank"] = df_filtered["dtf"].rank(method="min").astype(int)
    
    st.subheader("Current Rankings")

    render_rankings_table(df_filtered, target_boat)

    st.markdown("### Sailing Stats by Time Window")
    render_sailing_stats_table(df_filtered, target_boat)