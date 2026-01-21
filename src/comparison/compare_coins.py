import pandas as pd
from typing import List, Optional


def compare_assets(
    kpi_df: pd.DataFrame,
    assets: Optional[List[str]] = None,
    include_liquidity_concentration: bool = True
) -> pd.DataFrame:
    """
    Compare cryptocurrency assets side-by-side based on KPIs and provide a ranked score.

    Features:
    - Compare 2-5 assets (or all if not specified)
    - Add weighted scoring for combined ranking
    - Optionally include liquidity concentration in score
    - Format values for readability

    Args:
        kpi_df: DataFrame with KPI values (one row per asset)
        assets: Optional list of asset names to compare.
        include_liquidity_concentration: Whether to include liquidity concentration in ranking

    Returns:
        DataFrame with assets as rows, KPIs as columns, and ranking score
    """

    # Required KPI columns
    required_cols = ['asset', 'momentum', 'liquidity_proxy', 'volume_trend', 'downside_risk']
    if include_liquidity_concentration:
        required_cols += ['top5_share']  # from liquidity concentration

    missing_cols = [col for col in required_cols if col not in kpi_df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in KPI DataFrame: {missing_cols}")

    # Handle asset selection
    if assets is None:
        selected_assets = kpi_df['asset'].tolist()
    else:
        if not isinstance(assets, list):
            raise ValueError("assets parameter must be a list of asset names or None")
        selected_assets = [a for a in assets if a in kpi_df['asset'].unique()]
        if len(selected_assets) < 2:
            raise ValueError("Need at least 2 valid assets to compare")

    # Filter selected assets
    df = kpi_df[kpi_df['asset'].isin(selected_assets)].copy()

    # Fill missing or negative values with 0 to avoid computation issues
    for col in ['momentum', 'liquidity_proxy', 'volume_trend', 'downside_risk', 'top5_share']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: max(x, 0) if pd.notna(x) else 0)

    # Weighted scoring
    # Momentum (40%), Liquidity Proxy (30%), Downside Risk inverse (30%)
    # If liquidity concentration is included, reduce Liquidity Proxy weight to 20%, add 10% for liquidity health
    if include_liquidity_concentration and 'top5_share' in df.columns:
        df['weighted_score'] = (
            df['momentum'] * 0.4 +
            df['liquidity_proxy'] * 0.2 +
            df['downside_risk'].apply(lambda x: 100 - x) * 0.3 +  # lower downside = better
            (100 - df['top5_share'] * 100) * 0.1  # less concentration = better
        )
    else:
        df['weighted_score'] = (
            df['momentum'] * 0.4 +
            df['liquidity_proxy'] * 0.3 +
            df['downside_risk'].apply(lambda x: 100 - x) * 0.3
        )

    # Rank assets by score (descending)
    df = df.sort_values(by='weighted_score', ascending=False).reset_index(drop=True)
    df['Rank'] = df.index + 1

    # Select columns for display
    display_cols = [
        'asset', 'Rank', 'momentum', 'liquidity_proxy',
        'volume_trend', 'downside_risk'
    ]
    if include_liquidity_concentration and 'top5_share' in df.columns:
        display_cols.append('top5_share')

    comparison_df = df[display_cols].copy()

    # Formatting for readability
    comparison_df['momentum'] = comparison_df['momentum'].apply(lambda x: f"{x:.2f}%")
    comparison_df['volume_trend'] = comparison_df['volume_trend'].apply(lambda x: f"{x:.2f}%")
    comparison_df['liquidity_proxy'] = comparison_df['liquidity_proxy'].apply(lambda x: f"{x:,.2f}")
    comparison_df['downside_risk'] = comparison_df['downside_risk'].apply(lambda x: f"{x:.2f}%")
    if 'top5_share' in comparison_df.columns:
        comparison_df['top5_share'] = comparison_df['top5_share'].apply(lambda x: f"{x:.2%}")

    # Rename columns for display
    comparison_df.columns = [
        'Asset',
        'Rank',
        'Momentum (%)',
        'Liquidity Proxy',
        'Volume Trend (%)',
        'Downside Risk (%)'
    ] + (['Top-5 Liquidity Share'] if 'top5_share' in comparison_df.columns else [])

    return comparison_df
