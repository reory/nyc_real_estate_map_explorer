"""
This script takes a look at the csv file to make sure
the basemodel in USAProperty matches up with it.
"""

import pandas as pd

# Load just the first 5 rows to save memory
df = pd.read_csv("data/ny_properties_only.csv", nrows=20)

print("--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- DATA PREVIEW ---")
print(df.head())
