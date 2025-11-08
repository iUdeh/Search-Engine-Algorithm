# 5_test_search_ranking_finetuned.py
# Fine-tuned search scoring with tie-breakers, category boosts, and optional business signals

import pandas as pd
from rapidfuzz import fuzz

# Load products and boosts

products = pd.read_csv("products_with_inferred_categories.csv")  # your products CSV
category_boosts = pd.read_csv("category_boost_fixed.csv")       # your boost CSV

# Create boost dictionary (category -> boost)
boost_dict = {row['category'].lower(): row['boost'] for _, row in category_boosts.iterrows()}

# -----------------------
# Scoring function
# -----------------------------
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
    
    # Prefer exact word matches
    name_words = set(name.split())
    query_words = set(query.split())
    if query_words.issubset(name_words):
        base_score = min(base_score + 5, 100)
    
    # Apply category boost
    boost = boost_dict.get(category, 1.0)
    boost = max(1.0, min(boost, 3.0))  # Clamp between 1.0 and 3.0
    
    final_score = base_score * boost
    
    # Filter out noise
    if name_score < 20 and desc_score < 20:
        return 0
    
    return final_score

# -----------------------------
# Search function
# -----------------------------
def search(query, top_n=10):
    results_df = products.copy()
    results_df['score'] = results_df.apply(lambda x: score_product(x, query), axis=1)
    
    # Optional: tie-breakers by name alphabetically
    # Can also use business signals: popularity, price, etc., if available in CSV
    results = results_df[results_df['score'] > 0].sort_values(
        by=['score', 'name'],  # replace 'name' with 'popularity' or 'price' if present
        ascending=[False, True]
    ).head(top_n)
    
    return results[['name', 'category_final', 'score']]

# -----------------------------
# Run a test query
# -----------------------------
if __name__ == "__main__":
    query = input("Enter search query: ")
    top_results = search(query, top_n=10)
    
    print("\nTop search results:")
    print(top_results.to_string(index=False))
