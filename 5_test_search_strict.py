from rapidfuzz import fuzz
import pandas as pd

# Example: boost_dict from your CSV
boost_dict = pd.read_csv('category_boost_fixed.csv').set_index('category')['boost'].to_dict()

# Optional: query → category hints
CATEGORY_FILTERS = {
    'fryer': ['microwaves', 'kitchen'],
    'chair': ['chairs', 'furniture', 'office desks'],
    'wig': ['wigs', 'hair'],
    'jeans': ['fashion', 'trousers', 'jeans'],
    'samba': ['female shoes', 'male shoes', 'sports shoes']
}

# Minimum score thresholds per category
MIN_SCORE_THRESHOLDS = {
    'fashion': 80,
    'electronics': 85,
    'iphones': 60,
    'phones & tablets': 70,
    'default': 60
}

def score_product(product, query):
    name = str(product['name']).lower()
    desc = str(product.get('description', '')).lower()
    category = str(product.get('category_final', 'unknown')).lower()
    query = query.lower()

    # =========================
    # MULTI-TOKEN / COMPOUND QUERY FILTER
    # =========================
    query_tokens = query.split()
    name_tokens = name.split()
    
    if len(query_tokens) > 1:
        # Count how many query tokens have strong matches in product name
        matched_count = sum(
            1 for qt in query_tokens 
            if any(fuzz.ratio(qt, nt) > 85 for nt in name_tokens)
        )
        # Require 60% of query tokens to match
        if matched_count < len(query_tokens) * 0.6:
            return 0

    # =========================
    # SHORT QUERY STRICTNESS
    # =========================
    if len(query) <= 4:
        if fuzz.partial_ratio(query, name) < 75:
            return 0

    # =========================
    # BASE FUZZY SCORING
    # =========================
    name_score = fuzz.partial_ratio(query, name)
    desc_score = fuzz.partial_ratio(query, desc) if pd.notna(product.get('description')) else 0
    base_score = 0.85 * name_score + 0.15 * desc_score

    # Exact substring bonus
    if query in name:
        base_score = min(base_score + 15, 100)

    # Token match bonus
    has_strong_token_match = any(
        any(fuzz.ratio(qt, nt) > 85 for nt in name_tokens) for qt in query_tokens
    )
    if has_strong_token_match:
        base_score = min(base_score + 10, 100)

    # =========================
    # CATEGORY BOOST & CROSS-CATEGORY PENALTY
    # =========================
    boost = boost_dict.get(category, 1.0)
    boost = max(1.0, min(boost, 3.0))  # clamp

    # Apply category hint system
    for keyword, allowed_cats in CATEGORY_FILTERS.items():
        if keyword in query:
            if not any(allowed in category for allowed in allowed_cats):
                boost *= 0.2  # heavy penalty

    final_score = base_score * boost

    # =========================
    # MINIMUM SCORE THRESHOLDS
    # =========================
    min_score = MIN_SCORE_THRESHOLDS.get(category, MIN_SCORE_THRESHOLDS['default'])
    if final_score < min_score:
        return 0

    return final_score

def search(query, top_n=10):
    results_df = products.copy()
    results_df['score'] = results_df.apply(lambda x: score_product(x, query), axis=1)
    results = results_df[results_df['score'] > 0].sort_values(
        by=['score', 'name'], ascending=[False, True]
    ).head(top_n)
    return results[['name', 'category_final', 'score']]
