import pandas as pd
import numpy as np


def calculate_liquidity_concentration(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate liquidity concentration metrics for crypto assets.

    Metrics computed:
    1. Total traded volume per asset
    2. Top-5 volume concentration
    3. Top-5 volume share
    4. Liquidity health score (0–100)
    5. Concentration risk bucket (Low / Medium / High)

    Returns a DataFrame ready to merge with KPI outputs.
    """

    required_cols = {"asset", "volume"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns for liquidity analysis: {missing}")

    results = []

    for asset, group in df.groupby("asset"):
        volumes = group["volume"].dropna()

        if volumes.empty:
            results.append({
                "asset": asset,
                "total_volume": np.nan,
                "top5_volume": np.nan,
                "top5_share": np.nan,
                "liquidity_health": np.nan,
                "concentration_risk": "Unknown"
            })
            continue

        total_volume = volumes.sum()

        top5_volume = volumes.sort_values(ascending=False).head(5).sum()
        top5_share = top5_volume / total_volume if total_volume > 0 else np.nan

        # Liquidity Health Score (0–100)
        liquidity_health = (1 - top5_share) * 100 if pd.notna(top5_share) else np.nan

        # Risk classification
        if pd.isna(top5_share):
            risk = "Unknown"
        elif top5_share > 0.60:
            risk = "High"
        elif top5_share >= 0.40:
            risk = "Medium"
        else:
            risk = "Low"

        results.append({
            "asset": asset,
            "total_volume": round(total_volume, 2),
            "top5_volume": round(top5_volume, 2),
            "top5_share": round(top5_share, 4),
            "liquidity_health": round(liquidity_health, 2),
            "concentration_risk": risk
        })

    concentration_df = pd.DataFrame(results)

    # Rank assets by liquidity health (higher = better)
    concentration_df["liquidity_rank"] = (
        concentration_df["liquidity_health"]
        .rank(ascending=False, method="dense")
        .astype("Int64")
    )

    return concentration_df[
        [
            "asset",
            "total_volume",
            "top5_volume",
            "top5_share",
            "liquidity_health",
            "concentration_risk",
            "liquidity_rank",
        ]
    ]
