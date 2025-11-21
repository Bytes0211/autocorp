# Auto Parts Price Analysis
# Creation Date: 11/18/2025
# Last Modified: 11/18/2025
# Description: This script reads a CSV file containing auto parts sales data,
# cleans the 'Price' column by removing currency symbols and calculating
# average prices for ranges, and applies a markup to the prices.

import pandas as pd

df = pd.read_csv('sales-parts.csv')
print(df.head())
def format_price(price: str) -> float:
    price = price.replace('$', '')
    if 'each' in price:
        price = price.replace(' each', '')
    price = price.split('–')
    price = [float(p.strip()) for p in price] 
    average_price = (sum(price) / len(price)) * 1.05
    return average_price

df['Price'] = df['Price'].apply(format_price)
print(f'\n\n{df.head()}\n')
df.to_csv('auto-parts-clean.csv', index=False)
