"""
Interactive Search Engine Testing Suite
Run different testing modes to validate search quality
"""

import pandas as pd
from rapidfuzz import fuzz
import sys

# ==========================================
# LOAD YOUR SEARCH ALGORITHM
# ==========================================

# Load products and category boosts
products = pd.read_csv("products_with_inferred_categories.csv")
boost_dict = pd.read_csv('category_boost_fixed.csv').set_index('category')['boost'].to_dict()
boost_dict = {k.lower(): v for k, v in boost_dict.items()}

# Category filters
CATEGORY_FILTERS = {
    'fryer': ['microwaves', 'kitchen'],
    'chair': ['chairs', 'furniture', 'office desks'],
    'wig': ['wigs', 'hair', 'wigs and weaves'],
    'jeans': ['fashion', 'trousers', 'jeans'],
    'samba': ['female shoes', 'male shoes', 'sports shoes', 'shoes']
}

# Minimum score thresholds
MIN_SCORE_THRESHOLDS = {
    'fashion': 80,
    'electronics': 85,
    'iphones': 60,
    'phones & tablets': 70,
    'default': 60
}

# Brand blocking
BRAND_BLOCKS = {
    'samba': ['samsung', 'sam sung'],
}

def score_product(product, query):
    name = str(product['name']).lower()
    desc = str(product.get('description', '')).lower()
    category = str(product.get('category_final', 'unknown')).lower()
    query = query.lower()
    
    # Brand blocking
    if query in BRAND_BLOCKS:
        blocked_terms = BRAND_BLOCKS[query]
        if any(blocked in name for blocked in blocked_terms):
            return 0
    
    # Multi-token filter
    query_tokens = query.split()
    name_tokens = name.split()
    
    if len(query_tokens) > 1:
        matched_count = sum(
            1 for qt in query_tokens 
            if any(fuzz.ratio(qt, nt) > 85 for nt in name_tokens)
        )
        if matched_count < len(query_tokens) * 0.6:
            return 0
    
    # Short query strictness
    if len(query) <= 4:
        if fuzz.partial_ratio(query, name) < 75:
            return 0
    
    # Base fuzzy scoring
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
    
    # Category boost & cross-category penalty
    boost = boost_dict.get(category, 1.0)
    boost = max(1.0, min(boost, 3.0))
    
    for keyword, allowed_cats in CATEGORY_FILTERS.items():
        if keyword in query:
            if not any(allowed in category for allowed in allowed_cats):
                boost *= 0.2
    
    final_score = base_score * boost
    
    # Minimum score thresholds
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

# ==========================================
# TEST MODES
# ==========================================

def interactive_mode():
    """Single query testing - interactive"""
    print("\n" + "="*80)
    print("🔍 INTERACTIVE SEARCH MODE")
    print("="*80)
    print("Type 'quit' or 'exit' to return to menu\n")
    
    while True:
        query = input("Enter search query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        results = search(query, top_n=10)
        
        print(f"\n{'='*80}")
        print(f"Results for: '{query}'")
        print('='*80)
        
        if len(results) == 0:
            print("❌ No results found")
        else:
            print(f"✅ Found {len(results)} results\n")
            print(results.to_string(index=False))
            
            # Show category distribution
            cat_counts = results['category_final'].value_counts()
            print(f"\n📊 Category Distribution:")
            for cat, count in cat_counts.items():
                print(f"   {cat}: {count}")
        
        print()

def batch_test_mode():
    """Test multiple queries at once"""
    print("\n" + "="*80)
    print("📋 BATCH TEST MODE")
    print("="*80)
    
    test_queries = [
        "iphone",
        "samsung",
        "infinix",
        "tecno",
        "laptop",
        "air fryer",
        "chair",
        "wig",
        "jeans",
        "samba",
        "solar inverter",
        "fridge",
        "headphones",
        "charger",
        "shoes",
    ]
    
    print(f"\nTesting {len(test_queries)} queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        results = search(query, top_n=5)
        
        print(f"{i}. Query: '{query}'")
        if len(results) == 0:
            print("   ❌ No results\n")
        else:
            top_cat = results['category_final'].iloc[0]
            result_count = len(results)
            print(f"   ✅ {result_count} results | Top category: {top_cat}")
            print(f"   Top result: {results['name'].iloc[0][:60]}...\n")

def validation_mode():
    """Full validation with expected categories"""
    print("\n" + "="*80)
    print("🧪 VALIDATION MODE")
    print("="*80)
    
    test_queries = [
        "air fryer",
        "chair", 
        "wig",
        "samba",
        "jeans",
        "solar inverter",
        "fridge",
        "infinix",
        "tecno",
        "samsung",
        "iphone",
    ]
    
    INVALID_CATEGORIES = {
        "air fryer": ["iphones", "android phones", "phones & tablets"],
        "wig": ["iphones", "electronics", "phones & tablets"],
        "samba": ["android phones", "phones & tablets"],
        "chair": ["iphones", "electronics", "air purifiers"],
        "jeans": ["iphones", "electronics", "phones & tablets"],
        "solar inverter": ["iphones", "fashion", "shoes"],
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
    
    validation_df = pd.DataFrame(validation_results)
    print("\n" + validation_df.to_string(index=False))
    
    passed = len(validation_df[validation_df['status'] == '✅ PASS'])
    failed = len(validation_df[validation_df['status'] != '✅ PASS'])
    
    print("\n" + "="*80)
    print(f"📊 Results: {passed}/{len(test_queries)} passed ({passed/len(test_queries)*100:.0f}%)")
    print("="*80)

def detailed_analysis_mode():
    """Deep dive into a single query"""
    print("\n" + "="*80)
    print("🔬 DETAILED ANALYSIS MODE")
    print("="*80)
    
    query = input("\nEnter query to analyze: ").strip()
    
    if not query:
        return
    
    results = search(query, top_n=20)
    
    print(f"\n{'='*80}")
    print(f"Detailed Analysis: '{query}'")
    print('='*80)
    
    if len(results) == 0:
        print("❌ No results found")
        return
    
    print(f"\n✅ Found {len(results)} results")
    print(f"\n📊 Score Distribution:")
    print(f"   Highest: {results['score'].max():.2f}")
    print(f"   Lowest: {results['score'].min():.2f}")
    print(f"   Average: {results['score'].mean():.2f}")
    
    print(f"\n📁 Categories Found:")
    cat_counts = results['category_final'].value_counts()
    for cat, count in cat_counts.items():
        print(f"   {cat}: {count} products")
    
    print(f"\n🏆 Top 10 Results:")
    print(results.head(10).to_string(index=False))
    
    # Score buckets
    print(f"\n📈 Score Buckets:")
    buckets = {
        'Excellent (90-100)': len(results[results['score'] >= 90]),
        'Good (75-89)': len(results[(results['score'] >= 75) & (results['score'] < 90)]),
        'Fair (60-74)': len(results[(results['score'] >= 60) & (results['score'] < 75)]),
        'Weak (<60)': len(results[results['score'] < 60]),
    }
    for bucket, count in buckets.items():
        if count > 0:
            print(f"   {bucket}: {count}")

def compare_queries_mode():
    """Compare results across similar queries"""
    print("\n" + "="*80)
    print("⚖️  QUERY COMPARISON MODE")
    print("="*80)
    
    print("\nEnter queries to compare (one per line, empty line to finish):")
    queries = []
    while True:
        q = input(f"Query {len(queries)+1}: ").strip()
        if not q:
            break
        queries.append(q)
    
    if len(queries) < 2:
        print("Need at least 2 queries to compare")
        return
    
    print(f"\n{'='*80}")
    print("Comparison Results")
    print('='*80)
    
    for query in queries:
        results = search(query, top_n=5)
        print(f"\n🔍 '{query}'")
        if len(results) == 0:
            print("   No results")
        else:
            print(f"   Results: {len(results)} | Top score: {results['score'].iloc[0]:.1f}")
            print(f"   Categories: {', '.join(results['category_final'].unique()[:3])}")
            print(f"   Top result: {results['name'].iloc[0][:50]}...")

# ==========================================
# MAIN MENU
# ==========================================

def main():
    while True:
        print("\n" + "="*80)
        print("🔍 SEARCH ENGINE TEST SUITE")
        print("="*80)
        print("\nChoose a test mode:")
        print("  1. Interactive Mode - Search one query at a time")
        print("  2. Batch Test - Test multiple predefined queries")
        print("  3. Validation Mode - Full quality validation")
        print("  4. Detailed Analysis - Deep dive into one query")
        print("  5. Compare Queries - Compare multiple queries side-by-side")
        print("  6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            interactive_mode()
        elif choice == '2':
            batch_test_mode()
        elif choice == '3':
            validation_mode()
        elif choice == '4':
            detailed_analysis_mode()
        elif choice == '5':
            compare_queries_mode()
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        sys.exit(0)