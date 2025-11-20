import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducibility
np.random.seed(42)

# Read the CSV file
df = pd.read_csv('auto-parts-clean.csv')

# Add SKU column - 9 random alphanumeric characters
def generate_sku():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(np.random.choice(list(chars), 9))

df['sku'] = [generate_sku() for _ in range(len(df))]

# Add description column - combination of part_name and SKU separated by hyphen
df['description'] = df['part_name'] + '-' + df['sku']

# Add random date between Jan 1 2020 and Jul 15 2025
start_date = datetime(2020, 1, 1)
end_date = datetime(2025, 7, 15)
df['date'] = [fake.date_between(start_date=start_date, end_date=end_date) for _ in range(len(df))]

# Add vendor column - select from a list of automotive parts vendors
vendors = [
    'AutoZone',
    'Advanced Auto Parts',
    'O\'Reilly Auto Parts',
    'NAPA Auto Parts',
    'RockAuto',
    'CarQuest',
    'Pep Boys',
    'Summit Racing'
]
df['vendor'] = np.random.choice(vendors, size=len(df))

# Save to new CSV file
output_file = 'auto-parts-enhanced.csv'
df.to_csv(output_file, index=False)

print(f"Enhanced CSV saved to {output_file}")
print(f"\nFirst few rows:")
print(df.head())
print(f"\nDataset shape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
