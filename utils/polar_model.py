"""Polar model utilities for calculating boat efficiency and theoretical polars."""

import pandas as pd
import numpy as np


def build_polar_model(reports_df: pd.DataFrame, boat_id: str) -> pd.DataFrame:
    """
    Build a statistical polar model from historical data for a boat.

    Args:
        reports_df: Historical reports DataFrame
        boat_id: Boat ID to build model for

    Returns:
        DataFrame with model speeds by twa_bin and windspeed
    """
    boat_data = reports_df[
        (reports_df["boat"] == boat_id) & (reports_df["racestatus"] == "RAC")
    ].copy()

    if boat_data.empty:
        return pd.DataFrame()

    boat_data["heading"] = pd.to_numeric(boat_data["heading"], errors="coerce")
    boat_data["speed"] = pd.to_numeric(boat_data["speed"], errors="coerce")
    boat_data["windspeed"] = pd.to_numeric(boat_data["windspeed"], errors="coerce")
    boat_data["winddir"] = pd.to_numeric(boat_data["winddir"], errors="coerce")

    boat_data = boat_data.dropna(subset=["speed", "windspeed", "winddir"])
    boat_data = boat_data[boat_data["speed"] > 0]

    if boat_data.empty:
        return pd.DataFrame()

    boat_data["windspeed_kts"] = boat_data["windspeed"] / 10.0
    boat_data["twa"] = boat_data["winddir"]

    boat_data["twa_bin"] = (
        (boat_data["twa"] // 30).astype(int) * 30
    ).clip(upper=150).astype(int)

    model = boat_data.groupby(["twa_bin", "windspeed_kts"]).agg(
        model_speed=("speed", "mean"),
        count=("speed", "count"),
    ).reset_index()

    model = model[model["count"] >= 3]
    model = model.dropna()

    return model


def calculate_efficiency(
    current_speed: float,
    current_twa: float,
    current_windspeed: float,
    polar_model: pd.DataFrame,
) -> dict:
    """
    Calculate current efficiency compared to polar model.

    Args:
        current_speed: Current boat speed
        current_twa: Current true wind angle (from winddir column)
        current_windspeed: Current wind speed (in tenths, e.g., 138 = 13.8kts)
        polar_model: Polar model DataFrame from build_polar_model

    Returns:
        Dict with efficiency %, model_speed, twa
    """
    if polar_model.empty:
        return {"efficiency": None, "model_speed": None, "twa": None}

    windspeed_kts = current_windspeed / 10.0
    twa_bin = int(min(150, max(0, round(current_twa / 30) * 30)))

    model_row = polar_model[
        (polar_model["twa_bin"] == twa_bin) &
        (polar_model["windspeed_kts"].between(windspeed_kts - 2, windspeed_kts + 2))
    ]

    if model_row.empty:
        return {"efficiency": None, "model_speed": None, "twa": current_twa}

    model_speed = float(model_row["model_speed"].iloc[0])

    if model_speed <= 0:
        return {"efficiency": None, "model_speed": None, "twa": current_twa}

    efficiency = (current_speed / model_speed) * 100

    return {
        "efficiency": efficiency,
        "model_speed": model_speed,
        "twa": current_twa,
    }