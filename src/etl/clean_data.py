import pandas as pd
import numpy as np

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
