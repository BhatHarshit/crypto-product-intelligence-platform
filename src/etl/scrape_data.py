# src/etl/scrape_data.py
import requests
import pandas as pd

# Example endpoint (CoinGecko free API)
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    'vs_currency': 'usd',
    'order': 'market_cap_desc',
    'per_page': 200,
    'page': 1,
    'sparkline': False
}

response = requests.get(url, params=params).json()

# Convert to DataFrame
data = []
for coin in response:
    data.append({
        "name": coin["name"],
        "symbol": coin["symbol"].upper(),
        "price": coin["current_price"],
        "percent_change_1h": coin.get("price_change_percentage_1h_in_currency", 0),
        "percent_change_24h": coin.get("price_change_percentage_24h_in_currency", 0),
        "percent_change_7d": coin.get("price_change_percentage_7d_in_currency", 0),
        "volume_24h": coin["total_volume"],
        "market_cap": coin["market_cap"],
        "circulating_supply": coin["circulating_supply"]
    })

df = pd.DataFrame(data)
df.to_csv("data/crypto_data.csv", index=False)
print("Data scraped and saved to data/crypto_data.csv")
