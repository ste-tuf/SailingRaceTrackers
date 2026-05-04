"""Ranking current table component."""

import streamlit as st
import pandas as pd


def render(df_filtered, target_boat):
    df_filtered = df_filtered.copy()
    df_filtered["classType"] = df_filtered["category"].apply(
        lambda x: "Duo" if str(x).lower() == "duo" else "Solo"
    )

    df_filtered["classRank"] = (
        df_filtered.groupby("classType")["dtf"].rank(method="min").astype(int)
    )

    df_filtered["overallRank"] = df_filtered["dtf"].rank(method="min").astype(int)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Boats", len(df_filtered))
    col2.metric("Duo Boats", len(df_filtered[df_filtered["classType"] == "Duo"]))
    col3.metric(
        "Target DTF Rank",
        (
            df_filtered[
                df_filtered["boatName"].str.contains(target_boat, case=False, na=False)
            ]["overallRank"].min()
            if len(
                df_filtered[
                    df_filtered["boatName"].str.contains(target_boat, case=False, na=False)
                ]
            )
            > 0
            else "-"
        ),
    )

    display_df = df_filtered.copy()
    if target_boat:
        display_df["boatName"] = display_df["boatName"].apply(
            lambda x: f"⭐ {x}" if target_boat.lower() in str(x).lower() else x
        )

    display_df = display_df.sort_values("dtf")

    display_df = display_df.rename(
        columns={
            "overallRank": "Rank",
            "classType": "Class",
            "classRank": "Class Rank",
            "boatClass": "Boat Class",
            "dtf": "DTF",
            "dtl": "DTL",
        }
    )

    st.dataframe(
        display_df[
            ["Rank", "boatName", "Class", "Class Rank", "Boat Class", "DTF", "DTL"]
        ],
        width="stretch",
        height=600,
        hide_index=True,
    )

    return df_filtered