import pandas as pd

# Load dataset
df = pd.read_csv("../data/ai4i2020.csv")

# Drop unwanted columns
df = df.drop(['UDI', 'Product ID'], axis=1)

# Convert categorical
df['Type'] = df['Type'].map({'L':0, 'M':1, 'H':2})

# Remove nulls
df = df.dropna()

# Save cleaned data
df.to_csv("../data/cleaned_data.csv", index=False)

print("✅ Data Preprocessing Done")