import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

# =========================
# Load Cleaned Data
# =========================
data_path = 'data/crypto_data_clean.csv'
df = pd.read_csv(data_path)

# Ensure correct types
df['Price'] = df['Price'].astype(float)
df['1H %'] = df['1H %'].astype(float)
df['24H %'] = df['24H %'].astype(float)
df['7D %'] = df['7D %'].astype(float)
df['Volume(24H)'] = df['Volume(24H)'].astype(float)
df['MarketCap'] = df['MarketCap'].astype(float)
df['CirculatingSupply'] = df['CirculatingSupply'].astype(float)

# =========================
# TASK 1: Average Downfall KPI with Price Slicer
# =========================
price_bins = [0, 0.05, 0.5, 5, 50, np.inf]
price_labels = ['0-0.05', '0.05-0.5', '0.5-5', '5-50', '>50']
df['PriceRange'] = pd.cut(df['Price'], bins=price_bins, labels=price_labels)

# Average Downfall (1H, 24H, 7D)
df['AvgDownfall'] = (df['1H %'] + df['24H %'] + df['7D %']) / 3

# Example: select price range '0.5-5'
selected_range = '0.5-5'
df_task1 = df[df['PriceRange'] == selected_range].copy()
least_avg_downfall = df_task1.loc[df_task1['AvgDownfall'].idxmin()]

kpi_task1 = {
    'CoinName': least_avg_downfall['CoinName'],
    'Symbol': least_avg_downfall['Symbol'],
    'Price': least_avg_downfall['Price'],
    'AvgDownfall': least_avg_downfall['AvgDownfall'],
    'TotalCoins': len(df_task1)
}
print("=== TASK 1 KPI ===")
print(kpi_task1)

# =========================
# TASK 2: Top 10 coins 0-5 USD with 24H vs 7D price change
# =========================
df_task2 = df[(df['Price'] <= 5)]
df_task2['Price_24H_Ago'] = df_task2['Price'] / (1 + df_task2['24H %']/100)
df_task2['Price_7D_Ago'] = df_task2['Price'] / (1 + df_task2['7D %']/100)
df_top10_1H = df_task2.nlargest(10, '1H %')

# Chart: 24H vs 7D price
plt.figure(figsize=(10,5))
plt.plot(df_top10_1H['CoinName'], df_top10_1H['Price_24H_Ago'], label='Price 24H Ago', marker='o')
plt.plot(df_top10_1H['CoinName'], df_top10_1H['Price_7D_Ago'], label='Price 7D Ago', marker='o')
plt.xticks(rotation=45)
plt.ylabel('Price $')
plt.title('Top 10 Coins 0-5 USD: Price 24H vs 7D')
plt.legend()
plt.tight_layout()
plt.savefig('data/task2_price_chart.png')
plt.close()

# =========================
# TASK 3: Top 10 coins by 1H increase, slicer ranges <=10 and >10 USD
# =========================
df_task3 = df.copy()
range_condition = df_task3['Price'] <= 10
df_task3_top10 = df_task3[range_condition].nlargest(10, '1H %')
df_task3_top10.to_csv('data/task3_top10_price_change.csv', index=False)

# =========================
# TASK 4: Top 10 Volume coins (time-based display)
# =========================
current_hour = datetime.datetime.now().hour
if 9 <= current_hour < 17:
    df_task4_top10 = df.nlargest(10, 'Volume(24H)')
    df_task4_top10.to_csv('data/task4_top10_volume.csv', index=False)
else:
    print("[Please open in working hours (9AM to 5PM)]")

# =========================
# TASK 5: Compare Two Coins
# =========================
def compare_coins(coin1, coin2):
    # Input validation
    for coin in [coin1, coin2]:
        if len(coin) < 3 or len(coin) > 10 or any(char.isdigit() for char in coin):
            raise ValueError("Coin names must be 3-10 characters, no numbers")
    df1 = df[df['CoinName'] == coin1].iloc[0]
    df2 = df[df['CoinName'] == coin2].iloc[0]
    diff = {
        'VolumeDiff': df1['Volume(24H)'] - df2['Volume(24H)'],
        'MarketCapDiff': df1['MarketCap'] - df2['MarketCap'],
        'CirculatingSupplyDiff': df1['CirculatingSupply'] - df2['CirculatingSupply']
    }
    return diff

# Example
try:
    comparison_kpi = compare_coins(df['CoinName'].iloc[0], df['CoinName'].iloc[1])
    print("=== TASK 5 Comparison KPI ===")
    print(comparison_kpi)
except Exception as e:
    print(e)

# =========================
# TASK 6: Liquidity Pie Chart Top 5 vs Others
# =========================
price_slicer_condition = df['Price'] <= 50
df_sliced = df[price_slicer_condition].copy()
top5 = df_sliced.nlargest(5, 'Volume(24H)')
others_sum = df_sliced['Volume(24H)'].sum() - top5['Volume(24H)'].sum()

labels = list(top5['CoinName']) + ['Others']
sizes = list(top5['Volume(24H)']) + [others_sum]

plt.figure(figsize=(7,7))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
plt.title('Liquidity Distribution (Top 5 vs Others)')
plt.savefig('data/task6_liquidity_pie.png')
plt.close()

print("KPI calculations complete. CSVs and charts saved in data/")
