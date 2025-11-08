import pandas as pd

# Load your products dataset (with category_final and description)
products = pd.read_csv("products_with_inferred_categories.csv")

# Load category boosts
category_boosts = pd.read_csv("category_boost.csv")  # columns: category, boost

# ---- Helper scoring function ----
def score_product(product, query):
    """
    Computes a simple score for a single product.
    Score = text match count in name + description, multiplied by category boost.
    """
    name_match = query.lower() in str(product['name']).lower()
    desc_match = query.lower() in str(product['description']).lower()
    text_score = (name_match * 2) + (desc_match * 1)  # name weighted more than description
    
    # Get category boost
    category = str(product.get('category_final', 'Unknown'))
    boost_row = category_boosts[category_boosts['category'].str.lower() == category.lower()]
    boost = float(boost_row['boost'].values[0]) if not boost_row.empty else 1.0

    total_score = text_score * boost
    return total_score

# ---- Step 1: Check if iPhone products exist ----
iphone_products = products[products['name'].str.contains('iphone', case=False, na=False)]
print(f"✅ iPhone products found: {len(iphone_products)}")
if len(iphone_products) > 0:
    print(iphone_products[['name', 'category_final']].head(10))
print("-" * 80)

# ---- Step 2: Check top category boosts ----
print("🔝 Top 10 category boosts:")
print(category_boosts.sort_values('boost', ascending=False).head(10))
print("-" * 80)

# ---- Step 3: Test scoring manually ----
test_product = products.iloc[0]
score = score_product(test_product, "iphon")
print("🧪 Sample scoring test for first product:")
print(f"Name: {test_product['name']}")
print(f"Category: {test_product['category_final']}")
print(f"Score for query 'iphon': {score}")
print("-" * 80)

# ---- Step 4: Check for missing descriptions ----
missing_desc_count = products['description'].isna().sum()
print(f"⚠️ Products with missing descriptions: {missing_desc_count}")

# Optional: show some of them
if missing_desc_count > 0:
    print(products[products['description'].isna()][['name', 'category_final']].head(10))
