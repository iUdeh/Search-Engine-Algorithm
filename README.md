# 🧠 ChoCho Product Search Engine

A lightweight, intelligent **fuzzy search engine** built in **Python** for product discovery across diverse categories (electronics, fashion, furniture, etc.).  
It combines fuzzy string matching, category-aware scoring, and test-driven validation to deliver **fast**, **relevant**, and **cross-category-clean** search results.

## 🚀 Overview

This project powers a product search experience that mimics intelligent marketplace behavior — users can search for terms like _“infinix”_, _“jeans”_, or _“air fryer”_, and receive accurate, ranked product results based on **relevance**, **intent**, and **category weighting**.

The core algorithm leverages fuzzy matching and token-based weighting to find close textual matches in product names and categories, while penalizing irrelevant category overlaps.

## 🧩 Core Algorithm

The search algorithm uses a combination of the following:

1. **RapidFuzz Similarity Scoring**  
   Efficient string matching using `fuzz.token_set_ratio()` to calculate similarity between the user’s query and product attributes (`name`, `category_final`).

2. **Multi-token Matching**  
   For compound queries (e.g., “air fryer”), all tokens must appear across the name or category to avoid false positives.

3. **Category-Aware Boosting**  
   Matches that align with the correct category are **boosted**, while unrelated categories (e.g., _phones_ showing up for “wig”) are **penalized**.

4. **Minimum Score Thresholds**  
   Category-based score filters ensure only strong matches appear — e.g., electronics need ≥85 similarity score to qualify, while fashion items may need ≥80.

5. **Query Intent Detection (Planned)**  
   Future refinement will infer intent from the query (e.g., “jeans” → fashion intent, “fridge” → appliance intent) and automatically apply category biasing.

## 🧪 Validation System

A dedicated validation suite (`test_search_validation.py`) was created to test:
- Edge cases (e.g., “air fryer”, “wig”, “samba”)
- Brand searches (“infinix”, “tecno”, “iphone”)
- Category cross-contamination prevention  
- Multi-token accuracy

It produces a summary like:

     query  status                      top_3_categories                        issues
 air fryer  ✅ PASS            [kitchen, wigs and weaves]                          None
     samba ⚠️ FAIL          [android phones, male shoes] Contamination: android phones

## ⚙️ Dependencies

**Language:** Python 3.10+  

**Libraries:**
- `pandas` → Data manipulation & results aggregation  
- `rapidfuzz` → Fast fuzzy string comparison  
- `fuzzywuzzy` *(optional)* → Legacy matching (for testing only)  
- `pytest` *(optional)* → Unit test runner for CI/CD integration  

Install dependencies:

```bash
pip install pandas rapidfuzz

*chocho_search/*
│
├── products.csv                   # Product dataset (name, category_final)
├── search_engine.py                # Core search algorithm
├── test_search_validation.py       # Validation & contamination tests
└── README.md                       # Documentation

