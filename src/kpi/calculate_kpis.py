import pandas as pd
import numpy as np

def calculate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate key performance indicators for cryptocurrency assets.
    
    Computes exactly 4 KPIs:
    1. Momentum - Percentage price change over available window
    2. Liquidity Proxy - Rolling average of price × volume
    3. Volume Trend - Percentage change in volume
    4. Downside Risk - Standard deviation of negative returns only
    """

    required_cols = ['asset', 'price', 'volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns for KPI calculation: {missing_cols}")
    
    kpi_results = []
    
    for asset, group in df.groupby('asset'):
        if 'timestamp' in group.columns:
            group = group.sort_values('timestamp')
        
        kpi_dict = {'asset': asset}
        
        # 1. MOMENTUM
        if len(group) >= 2:
            first_price = group['price'].iloc[0]
            last_price = group['price'].iloc[-1]
            momentum = ((last_price - first_price) / first_price) * 100 if first_price > 0 else np.nan
        else:
            momentum = np.nan
        kpi_dict['momentum'] = momentum
        
        # 2. LIQUIDITY PROXY
        liquidity_values = group['price'] * group['volume']
        if len(liquidity_values) > 0:
            window_size = min(3, len(liquidity_values))
            rolling_liquidity = liquidity_values.rolling(window=window_size, min_periods=1).mean()
            liquidity_proxy = rolling_liquidity.mean()
        else:
            liquidity_proxy = np.nan
        kpi_dict['liquidity_proxy'] = liquidity_proxy
        
        # 3. VOLUME TREND
        if len(group) >= 2:
            first_volume = group['volume'].iloc[0]
            last_volume = group['volume'].iloc[-1]
            volume_trend = ((last_volume - first_volume) / first_volume) * 100 if first_volume > 0 else np.nan
        else:
            volume_trend = np.nan
        kpi_dict['volume_trend'] = volume_trend
        
        # 4. DOWNSIDE RISK
        if len(group) >= 2:
            returns = group['price'].pct_change()
            negative_returns = returns[returns < 0]
            downside_risk = negative_returns.std() * 100 if len(negative_returns) > 0 else 0.0
        else:
            downside_risk = np.nan
        kpi_dict['downside_risk'] = downside_risk
        
        kpi_results.append(kpi_dict)
    
    kpi_df = pd.DataFrame(kpi_results)
    kpi_df = kpi_df[['asset', 'momentum', 'liquidity_proxy', 'volume_trend', 'downside_risk']]
    
    numeric_cols = ['momentum', 'liquidity_proxy', 'volume_trend', 'downside_risk']
    kpi_df[numeric_cols] = kpi_df[numeric_cols].round(4)
    
    return kpi_df
