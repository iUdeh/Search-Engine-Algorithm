import pandas as pd
from rapidfuzz import fuzz

# Load products dataset
products = pd.read_csv("products_with_inferred_categories.csv")  # adjust path if needed

# Load category boosts
category_boosts = pd.read_csv("category_boost_fixed.csv")  # make sure this file exists
boost_dict = dict(zip(category_boosts['category'].str.lower(), category_boosts['boost']))

# Scoring function
def score_product(product, query):
    name = str(product['name']).lower()
    desc = str(product.get('description', '')).lower()
    category = str(product.get('category_final', 'unknown')).lower()
    query = query.lower()

    # Fuzzy matching
    name_score = fuzz.partial_ratio(query, name)
    desc_score = fuzz.partial_ratio(query, desc) if pd.notna(product.get('description')) else 0

    # Prioritize name heavily
    base_score = 0.85 * name_score + 0.15 * desc_score

    # Exact substring match bonus
    if query in name:
        base_score = min(base_score + 15, 100)

    # Apply category boost with clamp
    boost = boost_dict.get(category, 1.0)
    boost = max(1.0, min(boost, 3.0))

    final_score = base_score * boost

    # Filter out noise
    if name_score < 20 and desc_score < 20:
        return 0

    return final_score

# Search function
def search(query, top_n=10):
    results_df = products.copy()  # avoid modifying original
    results_df['score'] = results_df.apply(lambda x: score_product(x, query), axis=1)
    results = results_df[results_df['score'] > 0].sort_values('score', ascending=False).head(top_n)
    return results[['name', 'category_final', 'score']]

# Example test
query = "samsung"
top_results = search(query, top_n=10)
print(top_results)
