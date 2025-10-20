import json
import pandas as pd

# Load both JSON files
with open('fetched_data4.json', 'r', encoding='utf-8') as f:
    data1 = json.load(f)
with open('fetched_data5.json', 'r', encoding='utf-8') as f:
    data2 = json.load(f)

# Convert to DataFrames for easier comparison
df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

# Find differences
added = df2[~df2['text'].isin(df1['text'])]
removed = df1[~df1['text'].isin(df2['text'])]

print(f"✅ Added rows: {len(added)}")
print(f"❌ Removed rows: {len(removed)}")

if not added.empty:
    print("\nAdded examples:\n", added.head())
if not removed.empty:
    print("\nRemoved examples:\n", removed.head())
