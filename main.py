"""
Main entry point for crypto analytics platform.

This script demonstrates the end-to-end workflow:
1. Load data from CSV
2. Validate / prepare data
3. Calculate KPIs
4. Liquidity concentration analysis
5. Compare assets
"""

import pandas as pd
from pathlib import Path

def main():
    """Run the complete crypto analytics pipeline."""

    print("=" * 60)
    print("CRYPTO PRODUCT INTELLIGENCE PLATFORM")
    print("=" * 60)
    print()

    # Step 1: Load data
    print("Step 1: Loading data...")
    data_path = Path(__file__).parent / "data" / "crypto_data.csv"

    try:
        df_raw = pd.read_csv(data_path)
        print(f"✓ Loaded {len(df_raw)} rows from {data_path}")
        print(f"  Columns: {', '.join(df_raw.columns)}")
    except FileNotFoundError:
        print(f"✗ Error: Data file not found at {data_path}")
        return
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return

    print()

    # Step 2: Prepare / Clean data (schema-aware)
    print("Step 2: Preparing data...")

    try:
        # CASE 1: Product-grade dataset (snapshot-based)
        if "snapshot_time" in df_raw.columns:
            df_clean = df_raw.copy()

            # Create timestamp column for KPI compatibility
            df_clean["timestamp"] = pd.to_datetime(df_clean["snapshot_time"], errors="coerce")

            print("✓ Detected enriched snapshot dataset")
            print("✓ Skipped raw cleaning step")
            print(f"  Rows: {len(df_clean)}")
            print(f"  Unique assets: {df_clean['asset'].nunique()}")

        # CASE 2: Raw ingestion dataset
        else:
            from src.etl.clean_data import clean_crypto_data
            df_clean = clean_crypto_data(df_raw)

            print("✓ Raw data cleaned successfully")
            print(f"  Rows after cleaning: {len(df_clean)}")
            print(f"  Unique assets: {df_clean['asset'].nunique()}")

    except Exception as e:
        print(f"✗ Error during data preparation: {e}")
        return

    print()

    # Step 3: Calculate KPIs
    print("Step 3: Calculating KPIs...")
    try:
        from src.kpi.calculate_kpis import calculate_kpis
        kpi_df = calculate_kpis(df_clean)
        print(f"✓ KPIs calculated for {len(kpi_df)} assets")
        print()
        print("KPI Summary (sample):")
        print(kpi_df.head(10).to_string(index=False))
    except Exception as e:
        print(f"✗ Error during KPI calculation: {e}")
        return

    print()
    print("-" * 60)
    print()

    # Step 3.5: Liquidity concentration analysis
    print("Step 3.5: Analyzing liquidity concentration...")
    try:
        from src.analytics.liquidity_concentration import calculate_liquidity_concentration
        liquidity_df = calculate_liquidity_concentration(df_clean)

        print(f"✓ Liquidity concentration calculated for {len(liquidity_df)} assets")
        print()
        print("Liquidity Concentration Summary (Top 10):")
        print(liquidity_df.head(10).to_string(index=False))

        # Merge with KPI dataframe
        kpi_df = kpi_df.merge(liquidity_df, on="asset", how="left")

    except Exception as e:
        print(f"✗ Error during liquidity concentration analysis: {e}")
        return

    print()
    print("-" * 60)
    print()

    # Step 4: Compare assets
    print("Step 4: Comparing assets...")
    try:
        from src.comparison.compare_coins import compare_assets
        available_assets = kpi_df["asset"].tolist()
        assets_to_compare = available_assets[:5]

        comparison_df = compare_assets(kpi_df, assets=assets_to_compare)
        print("✓ Asset comparison complete")
        print()
        print("Asset Comparison:")
        print(comparison_df.to_string(index=False))

    except Exception as e:
        print(f"✗ Error during asset comparison: {e}")
        return

    print()
    print("=" * 60)
    print("✓ Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
