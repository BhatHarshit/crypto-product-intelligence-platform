import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def clean_crypto_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean cryptocurrency data:
    - Lowercase column names
    - Rename 'symbol' to 'asset' if needed
    - Convert timestamp to datetime
    - Ensure numeric types for price, volume, market_cap
    - Remove rows with missing essential columns
    - Remove negative values
    - Remove duplicates
    - Sort by asset and timestamp
    """
    df = df.copy()
    # Normalize columns
    df.columns = df.columns.str.lower().str.strip()
    
    # Rename symbol -> asset if needed
    if 'symbol' in df.columns and 'asset' not in df.columns:
        df.rename(columns={'symbol':'asset'}, inplace=True)
    
    # Check required columns
    required_cols = ['asset', 'timestamp', 'price', 'volume']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Numeric columns
    num_cols = ['price', 'volume']
    if 'market_cap' in df.columns:
        num_cols.append('market_cap')
    
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Drop rows with missing essential columns
    df = df.dropna(subset=required_cols)
    
    # Remove negative values
    for col in ['price','volume','market_cap']:
        if col in df.columns:
            df = df[df[col] >= 0]
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['asset','timestamp'])
    
    # Sort
    df = df.sort_values(by=['asset','timestamp']).reset_index(drop=True)
    
    return df

def expand_dataset(df: pd.DataFrame, total_assets: int = 200, days: int = 30) -> pd.DataFrame:
    """
    Expand dataset to total_assets with daily timestamps for given days.
    Existing assets are kept, new synthetic assets are added.
    """
    df = df.copy()
    
    # Existing assets
    existing_assets = df['asset'].unique().tolist()
    n_existing = len(existing_assets)
    
    # Generate synthetic assets
    synthetic_assets = [f"COIN{i}" for i in range(1, total_assets - n_existing + 1)]
    all_assets = list(existing_assets) + synthetic_assets
    
    # Generate timestamps
    start_date = pd.to_datetime('2024-01-01')
    timestamps = [start_date + timedelta(days=i) for i in range(days)]
    
    # Build expanded dataset
    expanded_rows = []
    for asset in all_assets:
        for ts in timestamps:
            # Randomized but realistic values
            if asset in existing_assets:
                base = df[df['asset'] == asset].iloc[0]
                price = base['price'] * np.random.uniform(0.95, 1.05)
                volume = base['volume'] * np.random.uniform(0.8, 1.2)
                market_cap = base['market_cap'] * np.random.uniform(0.95, 1.05)
            else:
                # Synthetic values
                price = round(np.random.uniform(0.1, 5000), 2)
                volume = int(np.random.uniform(1000000, 2000000000))
                market_cap = int(price * volume * np.random.uniform(0.5, 2))
            
            expanded_rows.append({
                'asset': asset,
                'timestamp': ts,
                'price': round(price, 2),
                'volume': int(volume),
                'market_cap': int(market_cap)
            })
    
    expanded_df = pd.DataFrame(expanded_rows)
    return expanded_df

if __name__ == "__main__":
    csv_path = "data/crypto_data.csv"
    df = pd.read_csv(csv_path)
    
    # Clean current dataset
    df_clean = clean_crypto_data(df)
    
    # Expand dataset to 200+ assets and 30 days of timestamps
    df_expanded = expand_dataset(df_clean, total_assets=200, days=30)
    
    # Clean again to ensure no issues
    df_final = clean_crypto_data(df_expanded)
    
    # Overwrite original CSV
    df_final.to_csv(csv_path, index=False)
    
    print(f"✅ Expanded & cleaned crypto data saved to {csv_path}")
    print(f"Rows: {len(df_final)}, Assets: {df_final['asset'].nunique()}")
