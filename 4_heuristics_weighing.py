import pandas as pd

# Load products dataset (CSV from previous steps)
products = pd.read_csv("products_with_inferred_categories.csv")  # <-- adjust path if needed

# Define strategic boosts
boosts = {
    'iphones': 2.5,
    'phones & tablets': 2.0,
    'phone accessories': 1.8,
    'tempered glass': 1.5,
    'phone cases': 1.5,
    'chargers': 1.5,
    'laptops': 1.8,
    'computers': 1.8,
    'electronics': 1.5,
    'fashion': 1.3,
    'default': 1.0  # Everything else
}

# Get all unique categories from your products
all_categories = products['category_final'].str.lower().unique()

# Create boost dataframe
boost_data = []
for cat in all_categories:
    boost = boosts.get(cat, boosts['default'])
    boost_data.append({'category': cat, 'boost': boost})

# Save to CSV
pd.DataFrame(boost_data).to_csv('category_boost_fixed.csv', index=False)

print("✅ category_boost_fixed.csv created successfully!")
