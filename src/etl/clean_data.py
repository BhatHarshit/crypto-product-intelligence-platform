# src/etl/clean_data.py
import pandas as pd

df = pd.read_csv("data/crypto_data.csv")

# Fill missing values
df.fillna(0, inplace=True)

# Ensure correct data types
df["price"] = df["price"].astype(float)
df["percent_change_1h"] = df["percent_change_1h"].astype(float)
df["percent_change_24h"] = df["percent_change_24h"].astype(float)
df["percent_change_7d"] = df["percent_change_7d"].astype(float)
df["volume_24h"] = df["volume_24h"].astype(float)
df["market_cap"] = df["market_cap"].astype(float)
df["circulating_supply"] = df["circulating_supply"].astype(float)

# Save cleaned data
df.to_csv("data/crypto_data_clean.csv", index=False)
print("Data cleaned and saved to data/crypto_data_clean.csv")
