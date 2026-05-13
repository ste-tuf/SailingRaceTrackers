"""Analysis tab - race analysis, history charts, and data processing."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import reports_to_dataframe, apply_filters


def render(rankings_df, selected_classes, target_boat, show_target_only, reports_df):
    df_filtered = apply_filters(rankings_df, selected_classes, target_boat, show_target_only)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Race Analysis")
        if not target_boat or target_boat not in rankings_df["boatName"].values:
            st.info("Select a target boat to analyze")
        else:
            target_row = rankings_df[rankings_df["boatName"].str.contains(target_boat, case=False, na=False)]
            if target_row.empty:
                st.info("Target boat not found in rankings")
            else:
                target_dtf = float(target_row["dtf"].iloc[0])
                df_plot = df_filtered.copy()
                df_plot["dtf_relative"] = df_plot["dtf"] - target_dtf
                df_plot["is_target"] = df_plot["boatName"].str.contains(target_boat, case=False, na=False)

                symbol_map = {False: "circle", True: "diamond-open"}
                df_plot["symbol"] = df_plot["is_target"].map(symbol_map)

                fig_speed = px.scatter(
                    df_plot,
                    x="dtf_relative",
                    y="speed",
                    color="boatClass",
                    hover_name="boatName",
                    size="rank",
                    symbol="symbol",
                    title=f"Current Speed vs Distance to Lead (0 = {target_boat})",
                )

                fig_speed.update_traces(marker=dict(size=14, line=dict(width=2, color="black")))
                fig_speed.update_layout(xaxis_title="Distance to Lead (NM)", yaxis_title="Current Speed (knots)")
                st.plotly_chart(fig_speed, width="stretch")
                fig_scatter = px.scatter(
                    df_plot,
                    x="dtf_relative",
                    y="dist24h",
                    color="boatClass",
                    hover_name="boatName",
                    size="rank",
                    symbol="symbol",
                    title=f"24h Speed vs Distance to Lead (0 = {target_boat})",
                )
                fig_scatter.update_traces(marker=dict(size=14, line=dict(width=2, color="black")))
                fig_scatter.update_layout(xaxis_title="Distance to Lead (NM)", yaxis_title="24h Speed (knots)")
                st.plotly_chart(fig_scatter, width="stretch")

    with col2:
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

    st.subheader("Estimated Polar")

    if not reports_df.empty and target_boat:
        target_id = str(
            rankings_df[
                rankings_df["boatName"].str.contains(target_boat, case=False, na=False)
            ]["boat"].iloc[0]
        )

        target_history = reports_df[
            (reports_df["boat"] == target_id) & (reports_df["racestatus"] == "RAC")
        ].copy()

        if not target_history.empty:
            target_history = target_history.copy()
            target_history["heading"] = pd.to_numeric(target_history["heading"], errors="coerce")
            target_history["winddir"] = pd.to_numeric(target_history["winddir"], errors="coerce")
            target_history["speed"] = pd.to_numeric(target_history["speed"], errors="coerce")
            target_history["windspeed"] = pd.to_numeric(target_history["windspeed"], errors="coerce")

            target_history = target_history.dropna(subset=["speed", "winddir"])
            target_history = target_history[target_history["speed"] > 0]

            if not target_history.empty:
                target_history["windspeed_kts"] = target_history["windspeed"] / 10.0
                target_history["twa"] = 180 - target_history["winddir"]

                target_history["wind_band"] = pd.cut(
                    target_history["windspeed_kts"],
                    bins=[0, 8, 12, 18, 25, 100],
                    labels=["0-8", "8-12", "12-18", "18-25", "25+"],
                    ordered=True,
                )

                fig_polar = px.scatter_polar(
                    target_history,
                    r="speed",
                    theta="twa",
                    color="wind_band",
                    title=f"{target_boat} Estimated Polar",
                )
                st.plotly_chart(fig_polar, width="stretch")

                st.subheader("Efficiency Model")

                target_history_model = target_history.copy()
                target_history_model["windspeed_kts"] = target_history_model["windspeed"] / 10.0
                target_history_model["twa"] = 180 - target_history_model["winddir"]

                target_history_model["twa_bin"] = (
                    (target_history_model["twa"] // 30).astype(int) * 30
                ).clip(upper=150).astype(int)

                polar_avg = target_history_model.groupby("twa_bin")["speed"].mean().reset_index()
                polar_avg.columns = ["twa_bin", "model_speed"]

                if not polar_avg.empty:
                    latest_row = rankings_df[rankings_df["boatName"].str.contains(target_boat, case=False, na=False)]
                    if not latest_row.empty:
                        latest_twa_orig = float(latest_row["winddir"].iloc[0]) if "winddir" in latest_row.columns else 0
                        latest_windspeed = float(latest_row["windspeed"].iloc[0]) if "windspeed" in latest_row.columns else 0
                        latest_speed = float(latest_row["speed"].iloc[0])

                        latest_twa = 180 - latest_twa_orig
                        latest_twa_bin = int(min(150, max(0, round(latest_twa / 30) * 30)))
                        model_row = polar_avg[polar_avg["twa_bin"] == latest_twa_bin]

                        if not model_row.empty:
                            model_speed = float(model_row["model_speed"].iloc[0])
                            efficiency = (latest_speed / model_speed * 100) if model_speed > 0 else None
                            if efficiency is not None:
                                st.metric(
                                    label=f"Current Efficiency ({latest_windspeed/10:.0f}kt, TWA {latest_twa:.0f}°)",
                                    value=f"{efficiency:.1f}%",
                                    delta=f"Speed: {latest_speed:.1f} / Model: {model_speed:.1f}",
                                )

                    efficiency_over_time = target_history.copy()
                    efficiency_over_time["timestamp"] = pd.to_datetime(efficiency_over_time["timestamp"])
                    efficiency_over_time = efficiency_over_time.sort_values("timestamp")

                    efficiency_over_time["windspeed_kts"] = efficiency_over_time["windspeed"] / 10.0
                    efficiency_over_time["twa"] = 180 - efficiency_over_time["winddir"]

                    efficiency_over_time["twa_bin"] = (
                        (efficiency_over_time["twa"] // 30).astype(int) * 30
                    ).clip(upper=150).astype(int)

                    efficiency_over_time = efficiency_over_time.merge(polar_avg, on="twa_bin", how="inner")

                    if not efficiency_over_time.empty:
                        efficiency_over_time["efficiency_pct"] = (
                            efficiency_over_time["speed"] / efficiency_over_time["model_speed"]
                        ) * 100
                        efficiency_over_time = efficiency_over_time.dropna(subset=["efficiency_pct"])
                        efficiency_over_time = efficiency_over_time.sort_values("timestamp")

                        fig_eff = px.line(
                            efficiency_over_time,
                            x="timestamp",
                            y="efficiency_pct",
                            title=f"{target_boat} Efficiency Over Time",
                        )
                        fig_eff.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="100%")
                        fig_eff.update_layout(yaxis_title="Efficiency (%)", hovermode="x unified")
                        st.plotly_chart(fig_eff, width="stretch")

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
