"""Analysis tab - race analysis, history charts, and data processing."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import glob
import os

from utils import process_and_archive, reports_to_dataframe, apply_filters


def render(rankings_df, selected_classes, target_boat, show_target_only, reports_df, data_dir):
    df_filtered = apply_filters(rankings_df, selected_classes, target_boat, show_target_only)
    
    st.subheader("Race Analysis")

    fig_scatter = px.scatter(
        rankings_df,
        x="dtf",
        y="speed",
        color="boatClass",
        hover_name="boatName",
        size="rank",
        title="Speed vs Distance to Finish",
    )
    st.plotly_chart(fig_scatter, width="stretch")

    st.subheader("Rank History")

    if not reports_df.empty:
        target_id = str(
            rankings_df[
                rankings_df["boatName"].str.contains(target_boat, case=False, na=False)
            ]["boat"].iloc[0]
        )

        target_history = reports_df[
            (reports_df["boat"] == target_id) & (reports_df["racestatus"] == "RAC")
        ].copy()

        if not target_history.empty:
            target_history = target_history.sort_values("timestamp")

            fig_rank = px.line(
                target_history,
                x="timestamp",
                y="rank",
                markers=True,
                title=f"{target_boat} Rank Over Time",
            )
            fig_rank.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_rank, width="stretch")

            fig_dtf = px.line(
                target_history,
                x="timestamp",
                y="dtf",
                markers=True,
                title=f"{target_boat} Distance to Finish Over Time",
            )
            st.plotly_chart(fig_dtf, width="stretch")

    st.subheader("Speed Over Time")

    if not reports_df.empty:
        reports_df = reports_df.copy()
        reports_df["timestamp"] = pd.to_datetime(reports_df["timestamp"])
        reports_df["boat"] = reports_df["boat"].astype(str)
        reports_df = reports_df[reports_df["racestatus"] == "RAC"]

        boat_names = dict(zip(rankings_df["boat"].astype(str), rankings_df["boatName"]))
        reports_df["boatName"] = reports_df["boat"].map(boat_names).fillna(reports_df["boat"])

        all_boats = sorted(reports_df["boatName"].unique())
        st.caption(f"Boat status: 🟢 RAC | 🔴 DNF | 🟠 RET | ⚪ STA")

        selected_boats = st.multiselect(
            "Select boats for speed chart",
            all_boats,
            default=all_boats[:5] if len(all_boats) > 5 else all_boats,
        )

        if selected_boats:
            filtered_df = reports_df[reports_df["boatName"].isin(selected_boats)]
            filtered_df = filtered_df.copy()

            boat_status = (
                filtered_df.groupby("boatName")
                .apply(
                    lambda x: (
                        x[x["racestatus"] != "STA"]["racestatus"].iloc[-1]
                        if len(x[x["racestatus"] != "STA"]) > 0
                        else "STA"
                    ),
                    include_groups=False,
                )
                .to_dict()
            )

            fig_speed = go.Figure()
            for boat_name in selected_boats:
                boat_df = filtered_df[filtered_df["boatName"] == boat_name]
                status = boat_status.get(boat_name, "STA")

                fig_speed.add_trace(
                    go.Scatter(
                        x=boat_df["timestamp"],
                        y=boat_df["speed"],
                        mode="lines+markers",
                        name=boat_name,
                        line=dict(
                            dash=(
                                "dot"
                                if status == "DNF"
                                else ("dash" if status == "RET" else "solid")
                            ),
                            color=(
                                "#888888"
                                if status == "DNF"
                                else ("#ff6b6b" if status == "RET" else None)
                            ),
                        ),
                        marker=dict(size=4),
                    )
                )

            fig_speed.update_layout(
                title="Speed Over Time (DNF/RET shown in grey/red)",
                yaxis_title="Speed (knots)",
                hovermode="x unified",
            )
            st.plotly_chart(fig_speed, width="stretch")
        else:
            st.info("Select at least one boat")
    else:
        st.info("No historical data available")

    st.subheader("Process Data")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Create Archive"):
            with st.spinner("Processing..."):
                try:
                    arch_path = process_and_archive(
                        config_path=f"{data_dir}/config.json",
                        boats_json_path=f"{data_dir}/boats.json",
                        tracks_json_path=f"{data_dir}/tracks.json",
                        output_dir=f"{data_dir}/processed",
                    )
                    st.success(f"Archive: {os.path.basename(arch_path)}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        archives = sorted(glob.glob(f"{data_dir}/processed/*.json"), reverse=True)
        if archives:
            st.caption(f"Latest: {os.path.basename(archives[0])}")