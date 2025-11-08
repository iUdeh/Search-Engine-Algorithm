# ChoCho Search Engine 🛒🔍

## Project Overview
ChoCho Search Engine is a Python-based product search system designed to provide accurate, relevance-weighted results for an e-commerce catalog. It combines fuzzy string matching, category boosts, and cross-category filtering to return precise results, even for typos, multi-word queries, and short or ambiguous search terms. The search engine is designed for easy testing, evaluation, and refinement with edge cases in mind.

Core features include:
- Fuzzy matching using **RapidFuzz**
- Token-level multi-word query handling (e.g., "air fryer" matches only relevant products)
- Category boosts to prioritize certain product types
- Cross-category noise suppression
- Brand blocking to prevent misleading matches
- Minimum score thresholds to filter weak matches
- Interactive, batch, validation, detailed analysis, and comparison modes

## Algorithm Summary
The scoring and ranking logic is designed to maximize relevance and reduce noise:

1. **Tokenization & Multi-Word Handling**: Queries with multiple words require at least 60% of tokens to match product names.
2. **Fuzzy Scoring**: Base score is 85% name match and 15% description match using RapidFuzz partial ratio.
3. **Exact Match & Token Bonuses**: Adds extra points if the query is a substring of the product name or if query tokens have strong matches.
4. **Category Boost & Cross-Category Penalty**: Products in boosted categories get a multiplier (1–3x). Products outside relevant categories for a query are heavily penalized.
5. **Short Query Strict Filtering**: Queries of ≤4 characters require higher similarity to avoid false positives.
6. **Minimum Score Thresholds**: Each category has a minimum score threshold to ensure only strong matches appear.

## Dependencies
- **Python 3.10+**
- Libraries:
  - `pandas` → for data manipulation
  - `rapidfuzz` → for fuzzy string matching
- Optional:
  - `git` → version control

Install dependencies using:
```bash
pip install pandas rapidfuzz
chocho_search/
├─ products_with_inferred_categories.csv    # Product catalog
├─ category_boost_fixed.csv                 # Category boost mapping
├─ search_engine.py                         # Main search & scoring algorithm
├─ test_search_validation.py                # Automated validation suite
└─ README.md                                # Project documentation

1. Getting Started
Clone the repository
git clone <your-repo-url>
cd chocho_search


2. Set up Python environment
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate
pip install pandas rapidfuzz

3. Prepare datasets
Place the following CSV files in the project root:
products_with_inferred_categories.csv → the full product catalog
category_boost_fixed.csv → optional category boost values

4. Run the search engine
python search_engine.py

5. Use the interactive menu

Interactive Mode – Type queries manually

Batch Test – Run multiple predefined queries for evaluation

Validation Mode – Checks for contamination & edge cases

Detailed Analysis – Shows scores, top results, and categories

Compare Queries – Compare results across multiple queries

Exit – Quit the test suite

Example Validation Output

Sample run of validation mode (top 10 results per query):

🧪 SEARCH VALIDATION RESULTS
================================================================================
         query  status                      top_3_categories                        issues
     air fryer  ✅ PASS            [kitchen, microwaves]                          None
         chair  ✅ PASS [furniture, chairs, office desks]                          None
           wig  ✅ PASS      [wigs and weaves, hair]                          None
         samba ⚠️ FAIL          [male shoes, electronics] Contamination: electronics
         jeans  ✅ PASS                             [fashion, trousers]                          None
solar inverter  ✅ PASS                           [inverters, electronics]                          None
        fridge  ✅ PASS                       [refrigerators, electronics]                          None
        iphone  ✅ PASS                             [iphones]                          None
================================================================================
📊 Results: 7/8 passed (88%)
================================================================================
