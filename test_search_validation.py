# test_search_validation_full.py
import pandas as pd
from rapidfuzz import fuzz

# ==========================================
# BOOST CONFIGURATION
# ==========================================
boost_dict = {
    "iphones": 1.5,
    "android phones": 1.5,
    "mobile phones": 1.4,
    "fashion": 1.2,
    "electronics": 1.0,
    "inverters": 1.1,
    "refrigerators": 1.1,
    "wigs and weaves": 1.3,
    "furniture": 1.1,
}

# ==========================================
# SCORING FUNCTION
# ==========================================
def score_product(product, query):
    name = str(product.get('name', '')).lower()
    desc = str(product.get('description', '')).lower()
    category = str(product.get('category_final', 'unknown')).lower()
    query = query.lower()

    # --- fuzzy match scores ---
    name_score = fuzz.partial_ratio(query, name)
    desc_score = fuzz.partial_ratio(query, desc) if desc else 0

    # --- token matching ---
    query_tokens = set(query.split())
    name_tokens = set(name.split())
    desc_tokens = set(desc.split())

    has_strong_token_match = any(
        fuzz.ratio(qt, nt) > 85 for qt in query_tokens for nt in name_tokens
    )

    # --- strict filter ---
    if name_score < 60 and not has_strong_token_match:
        if len(query_tokens) == 1 or desc_score < 60:
            return 0

    boost = max(1.0, min(boost_dict.get(category, 1.0), 3.0))
    if boost > 2.0 and name_score < 70 and not has_strong_token_match:
        return 0

    # --- base scoring ---
    base_score = 0.85 * name_score + 0.15 * desc_score
    if query in name:
        base_score = min(base_score + 15, 100)
    if has_strong_token_match:
        base_score = min(base_score + 10, 100)

    # --- apply boost ---
    final_score = base_score * boost
    return final_score


# ==========================================
# SEARCH FUNCTION
# ==========================================
def search(query, top_n=10):
    # Example mock dataset
    data = [
        {"name": "iPhone 14 Pro", "description": "Apple smartphone", "category_final": "iphones"},
        {"name": "Samsung Galaxy A14", "description": "Android phone", "category_final": "android phones"},
        {"name": "Air Fryer 4L", "description": "Kitchen appliance", "category_final": "kitchen"},
        {"name": "Office Chair", "description": "Ergonomic swivel chair", "category_final": "furniture"},
        {"name": "Samba Classic", "description": "Adidas male shoes", "category_final": "male shoes"},
        {"name": "Human Hair Wig", "description": "Curly lace front wig", "category_final": "wigs and weaves"},
        {"name": "Solar Inverter 2.5kVA", "description": "Power backup inverter", "category_final": "inverters"},
        {"name": "Jeans Denim Blue", "description": "Men's casual fashion jeans", "category_final": "fashion"},
        {"name": "LG Fridge", "description": "Double door refrigerator", "category_final": "refrigerators"},
    ]
    df = pd.DataFrame(data)

    df["score"] = df.apply(lambda x: score_product(x, query), axis=1)
    df = df[df["score"] > 0].sort_values("score", ascending=False).head(top_n)
    return df


# ==========================================
# VALIDATION TESTS
# ==========================================
test_queries = [
    "air fryer",
    "chair",
    "wig",
    "samba",
    "jeans",
    "solar inverter",
    "fridge",
    "iphone",
]

INVALID_CATEGORIES = {
    "air fryer": ["iphones", "android phones", "shoes", "fashion"],
    "wig": ["iphones", "electronics", "microwaves"],
    "samba": ["iphones", "android phones", "phones & tablets"],
    "chair": ["iphones", "air purifiers", "jump ropes"],
    "jeans": ["iphones", "electronics", "microwaves"],
    "solar inverter": ["iphones", "fashion", "shoes", "wigs"],
    "fridge": ["iphones", "fashion", "shoes"],
}

validation_results = []

for query in test_queries:
    results = search(query, top_n=10)
    if len(results) == 0:
        validation_results.append({
            "query": query,
            "status": "❌ NO RESULTS",
            "top_3_categories": [],
            "issues": "No products found"
        })
        continue

    top_cats = results['category_final'].str.lower().unique().tolist()
    invalid_cats = [cat.lower() for cat in INVALID_CATEGORIES.get(query, [])]
    contamination = [cat for cat in top_cats if cat in invalid_cats]

    if contamination:
        status = "⚠️ FAIL"
        issues = f"Contamination: {', '.join(contamination)}"
    else:
        status = "✅ PASS"
        issues = None

    validation_results.append({
        "query": query,
        "status": status,
        "top_3_categories": top_cats[:3],
        "issues": issues
    })

# ==========================================
# RESULTS SUMMARY
# ==========================================
validation_df = pd.DataFrame(validation_results)
print("\n" + "="*80)
print("🧪 SEARCH VALIDATION RESULTS")
print("="*80)
print(validation_df.to_string(index=False))
passed = len(validation_df[validation_df['status'] == '✅ PASS'])
failed = len(validation_df[validation_df['status'] != '✅ PASS'])
print("\n" + "="*80)
print(f"📊 Results: {passed}/{len(test_queries)} passed ({passed/len(test_queries)*100:.0f}%)")
print("="*80)
