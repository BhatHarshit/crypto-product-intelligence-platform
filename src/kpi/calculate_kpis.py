import pandas as pd
import numpy as np

def calculate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Product-grade KPI engine for crypto assets.

    Existing KPIs (kept for backward compatibility):
    - momentum
    - liquidity_proxy
    - volume_trend
    - downside_risk

    New KPIs (enterprise-grade):
    - momentum_1h, momentum_24h, momentum_7d
    - avg_downside_risk_pct
    - liquidity_score
    - avg_volume
    - market_cap_tier
    """

    required_cols = ['asset', 'price', 'volume', 'timestamp']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column for KPI calculation: {col}")

    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['asset', 'timestamp'])

    kpi_results = []

    for asset, group in df.groupby('asset'):
        group = group.sort_values('timestamp')
        kpi = {'asset': asset}

        # ----------------------------
        # 1. OVERALL MOMENTUM (existing)
        # ----------------------------
        if len(group) >= 2:
            first_price = group['price'].iloc[0]
            last_price = group['price'].iloc[-1]
            kpi['momentum'] = ((last_price - first_price) / first_price) * 100 if first_price > 0 else np.nan
        else:
            kpi['momentum'] = np.nan

        # ----------------------------
        # 2. MULTI-TIMEFRAME MOMENTUM
        # ----------------------------
        def timeframe_momentum(hours):
            cutoff = group['timestamp'].max() - pd.Timedelta(hours=hours)
            sub = group[group['timestamp'] >= cutoff]
            if len(sub) >= 2:
                p0, p1 = sub['price'].iloc[0], sub['price'].iloc[-1]
                return ((p1 - p0) / p0) * 100 if p0 > 0 else np.nan
            return np.nan

        kpi['momentum_1h'] = timeframe_momentum(1)
        kpi['momentum_24h'] = timeframe_momentum(24)
        kpi['momentum_7d'] = timeframe_momentum(168)

        # ----------------------------
        # 3. LIQUIDITY PROXY (existing)
        # ----------------------------
        liquidity_values = group['price'] * group['volume']
        kpi['liquidity_proxy'] = liquidity_values.rolling(
            window=min(3, len(liquidity_values)), min_periods=1
        ).mean().mean()

        # ----------------------------
        # 4. LIQUIDITY SCORE (normalized)
        # ----------------------------
        kpi['liquidity_score'] = np.log(group['volume'].mean()) if group['volume'].mean() > 0 else np.nan

        # ----------------------------
        # 5. VOLUME METRICS
        # ----------------------------
        kpi['avg_volume'] = group['volume'].mean()

        if len(group) >= 2:
            v0, v1 = group['volume'].iloc[0], group['volume'].iloc[-1]
            kpi['volume_trend'] = ((v1 - v0) / v0) * 100 if v0 > 0 else np.nan
        else:
            kpi['volume_trend'] = np.nan

        # ----------------------------
        # 6. DOWNSIDE RISK (existing)
        # ----------------------------
        returns = group['price'].pct_change()
        negative_returns = returns[returns < 0]
        kpi['downside_risk'] = negative_returns.std() * 100 if len(negative_returns) > 0 else 0.0

        # ----------------------------
        # 7. AVG DOWNFALL RISK (product-grade)
        # ----------------------------
        kpi['avg_downside_risk_pct'] = abs(negative_returns.mean() * 100) if len(negative_returns) > 0 else 0.0

        # ----------------------------
        # 8. MARKET CAP TIER
        # ----------------------------
        if 'market_cap' in group.columns:
            avg_mcap = group['market_cap'].mean()
            if avg_mcap >= 100_000_000_000:
                tier = 'Large Cap'
            elif avg_mcap >= 10_000_000_000:
                tier = 'Mid Cap'
            else:
                tier = 'Small Cap'
        else:
            tier = 'Unknown'

        kpi['market_cap_tier'] = tier

        kpi_results.append(kpi)

    kpi_df = pd.DataFrame(kpi_results)

    # Round numeric columns for presentation
    numeric_cols = kpi_df.select_dtypes(include=[np.number]).columns
    kpi_df[numeric_cols] = kpi_df[numeric_cols].round(4)

    return kpi_df
