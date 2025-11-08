import pandas as pd

# Load enriched dataset from Step 1
df = pd.read_csv("products_with_inferred_categories.csv")

# Step 1: Normalize category names
df["category_final"] = df["category_final"].str.strip().str.lower()

# Step 2: Profile category distribution
category_counts = df["category_final"].value_counts()
total_products = len(df)

print(f"Total products: {total_products}\n")
print("Category distribution (top 30):")
print(category_counts.head(30))

# Step 3: Identify underrepresented and overrepresented categories
# Underrepresented: <1% of total products
underrepresented = category_counts[category_counts / total_products < 0.01]
# Overrepresented: >20% of total products
overrepresented = category_counts[category_counts / total_products > 0.2]

print("\n⚠️ Underrepresented categories (<1% of total):")
print(underrepresented)

print("\n⚠️ Overrepresented categories (>20% of total):")
print(overrepresented)

# Step 4: Optional CSV export for inspection
df.to_csv("products_balanced_profile.csv", index=False)
print("\n💾 Exported products_balanced_profile.csv for review")
