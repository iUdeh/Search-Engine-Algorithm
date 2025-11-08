# explore_products.py

import pandas as pd
from sqlalchemy import create_engine

# ------------------------------
# 1. Database connection
# ------------------------------
user = "chocho_analyst"
password = "ChoCho2025!Analytics#ReadOnly"
host = "ep-polished-night-aev76ljb.c-2.us-east-2.aws.neon.tech"
port = 5432
database = "neondb"

# Create SQLAlchemy engine
engine = create_engine(
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
)

# ------------------------------
# 2. Pull full products dataset with category names
# ------------------------------
query = """
SELECT 
    p.id,
    p.name,
    p.description,
    p.category_id,
    c.name AS category_name,
    p.brand_id,
    p.specifications,
    p.status,
    p.price
FROM products p
LEFT JOIN categories c
ON p.category_id = c.id;
"""

# Load into pandas DataFrame
df = pd.read_sql_query(query, engine)

# ------------------------------
# 3. Inspect dataset shape
# ------------------------------
print(f"Total products: {df.shape[0]}")
print(f"Total columns: {df.shape[1]}\n")

# ------------------------------
# 4. Check missing/null fields
# ------------------------------
print("Missing/null values per column:")
print(df.isnull().sum(), "\n")

# ------------------------------
# 5. Preview first 20 rows
# ------------------------------
print("Sample products (first 20 rows):")
print(df.head(20), "\n")

# ------------------------------
# 6. Analyze category distribution
# ------------------------------
print("Category distribution (top 20 categories):")
category_counts = df['category_name'].value_counts()
print(category_counts.head(20), "\n")

# ------------------------------
# 7. Clean category names for search
# ------------------------------
df['category_name_clean'] = (
    df['category_name']
    .fillna("unknown")  # handle missing categories
    .str.lower()        # lowercase
    .str.strip()        # remove leading/trailing whitespace
    .str.replace(r'\s+', ' ', regex=True)           # normalize spaces
    .str.replace(r'[^\w\s]', '', regex=True)       # remove special characters
)

print("Cleaned category names (unique values):")
print(df['category_name_clean'].unique(), "\n")

# ------------------------------
# 8. Optional: Preview product names/descriptions
# ------------------------------
df['name_clean'] = df['name'].fillna("").str.lower().str.strip()
df['description_clean'] = df['description'].fillna("").str.lower().str.strip()

print("Sample cleaned product names and descriptions:")
print(df[['name_clean', 'description_clean']].head(10))

# Export current data to CSV for next step
df.to_csv("products_clean.csv", index=False)
print("✅ Exported cleaned data to products_clean.csv")
