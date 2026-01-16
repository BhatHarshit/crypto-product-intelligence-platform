"import pandas as pd
import numpy as np
from typing import List, Optional


def compare_assets(
    kpi_df: pd.DataFrame,
    assets: Optional[List[str]] = None
) -> pd.DataFrame:
    \"\"\"
    Compare cryptocurrency assets side-by-side based on their KPIs.
    
    Responsibilities:
    - Compare 2-5 assets (or all if not specified)
    - Produce side-by-side KPI values
    - Handle invalid asset input gracefully
    - Return clean, human-readable DataFrame
    
    Args:
        kpi_df: DataFrame with KPI values (one row per asset)
        assets: Optional list of 2-5 asset names to compare.
                If None, compares all assets (limited to first 5)
    
    Returns:
        DataFrame with assets as rows and KPIs as columns for comparison
        
    Assumptions:
    - kpi_df has columns: asset, momentum, liquidity_proxy, volume_trend, downside_risk
    - If assets list provided, will filter to those assets only
    - Invalid assets in the list are skipped with a warning
    - No plotting (returns data only)
    \"\"\"
    
    # Validate input DataFrame
    required_cols = ['asset', 'momentum', 'liquidity_proxy', 'volume_trend', 'downside_risk']
    missing_cols = [col for col in required_cols if col not in kpi_df.columns]
    if missing_cols:
        raise ValueError(f\"Missing required columns in KPI DataFrame: {missing_cols}\")
    
    # Handle asset selection
    if assets is None:
        # Compare all assets, limited to first 5
        selected_assets = kpi_df['asset'].head(5).tolist()
        if len(kpi_df) > 5:
            print(f\"Note: Comparing first 5 assets out of {len(kpi_df)} available\")
    else:
        # Validate assets list
        if not isinstance(assets, list):
            raise ValueError(\"assets parameter must be a list of asset names or None\")
        
        if len(assets) < 2:
            raise ValueError(\"Must compare at least 2 assets\")
        
        if len(assets) > 5:
            print(f\"Warning: More than 5 assets provided ({len(assets)}), using first 5\")
            assets = assets[:5]
        
        # Check which assets exist in the data
        available_assets = kpi_df['asset'].unique()
        selected_assets = []
        invalid_assets = []
        
        for asset in assets:
            if asset in available_assets:
                selected_assets.append(asset)
            else:
                invalid_assets.append(asset)
        
        # Handle invalid assets gracefully
        if invalid_assets:
            print(f\"Warning: The following assets were not found and will be skipped: {invalid_assets}\")
        
        if len(selected_assets) < 2:
            raise ValueError(
                f\"Not enough valid assets to compare. \"
                f\"Found {len(selected_assets)} valid assets, need at least 2. \"
                f\"Available assets: {', '.join(available_assets)}\"
            )
    
    # Filter to selected assets
    comparison_df = kpi_df[kpi_df['asset'].isin(selected_assets)].copy()
    
    # Sort by asset name for consistent ordering
    comparison_df = comparison_df.sort_values('asset').reset_index(drop=True)
    
    # Reorder columns for better readability: asset first, then KPIs
    column_order = [
        'asset',
        'momentum',
        'liquidity_proxy',
        'volume_trend',
        'downside_risk'
    ]
    comparison_df = comparison_df[column_order]
    
    # Add ranking information for each KPI (optional enhancement for readability)
    # Higher momentum is better, lower downside risk is better
    comparison_df['momentum_rank'] = comparison_df['momentum'].rank(ascending=False, method='min').astype(int)
    comparison_df['liquidity_rank'] = comparison_df['liquidity_proxy'].rank(ascending=False, method='min').astype(int)
    comparison_df['volume_trend_rank'] = comparison_df['volume_trend'].rank(ascending=False, method='min').astype(int)
    comparison_df['risk_rank'] = comparison_df['downside_risk'].rank(ascending=True, method='min').astype(int)
    
    # Create a clean display version
    # Main comparison table without ranks
    main_comparison = comparison_df[[
        'asset',
        'momentum',
        'liquidity_proxy',
        'volume_trend',
        'downside_risk'
    ]].copy()
    
    # Format for better human readability
    main_comparison['momentum'] = main_comparison['momentum'].apply(
        lambda x: f\"{x:.2f}%\" if pd.notna(x) else \"N/A\"
    )
    main_comparison['volume_trend'] = main_comparison['volume_trend'].apply(
        lambda x: f\"{x:.2f}%\" if pd.notna(x) else \"N/A\"
    )
    main_comparison['liquidity_proxy'] = main_comparison['liquidity_proxy'].apply(
        lambda x: f\"{x:,.2f}\" if pd.notna(x) else \"N/A\"
    )
    main_comparison['downside_risk'] = main_comparison['downside_risk'].apply(
        lambda x: f\"{x:.2f}%\" if pd.notna(x) else \"N/A\"
    )
    
    # Rename columns for clarity
    main_comparison.columns = [
        'Asset',
        'Momentum (%)',
        'Liquidity Proxy',
        'Volume Trend (%)',
        'Downside Risk (%)'
    ]
    
    return main_comparison
"