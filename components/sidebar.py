"""Sidebar component for filter controls."""

import streamlit as st
from datetime import datetime


def render(rankings_df, latest_timestamp, race_state):
    """Render sidebar with filters.
    
    Stores filter values in st.session_state:
    - target_boat
    - selected_classes
    - show_target_only
    """
    st.sidebar.header("Settings")

    if latest_timestamp:
        try:
            dt = datetime.fromisoformat(latest_timestamp.replace("Z", "+00:00"))
            formatted_date = dt.strftime("%b %d, %Y at %H:%M")
        except:
            formatted_date = latest_timestamp
    else:
        formatted_date = "Unknown"

    st.sidebar.markdown(f"**📅 Last Update:** {formatted_date}")
    st.sidebar.markdown(f"**🏁 Race State:** {race_state}")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")

    all_boat_names = [""] + sorted(rankings_df["boatName"].dropna().unique().tolist())
    st.session_state.target_boat = st.sidebar.selectbox(
        "Target Boat", 
        all_boat_names, 
        index=all_boat_names.index("TUF TUF") if "TUF TUF" in all_boat_names else 0
    )

    all_classes = sorted(rankings_df["boatClass"].dropna().unique().tolist())
    st.session_state.selected_classes = st.sidebar.multiselect("Boat Class", all_classes, default=[])

    st.session_state.show_target_only = st.sidebar.checkbox("Show Target Boat Only", value=False)

    st.sidebar.markdown("---")
    st.sidebar.caption("Sailing Race Tracker | Python + Streamlit")

    return st.session_state.target_boat, st.session_state.selected_classes, st.session_state.show_target_only