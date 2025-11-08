import pandas as pd
import re

# Load the exported dataset
df = pd.read_csv("products_clean.csv")

print(f"Total products: {len(df)}")
print(f"Missing category_name before: {df['category_name'].isna().sum()}")

# Define keyword → category mapping
category_map = {
    r"\biphone|apple\b": "iPhones",
    r"\bsamsung|infinix|tecno|xiaomi|itel|oppo|android\b": "Android Phones",
    r"\blaptop|macbook|hp|dell|lenovo|notebook|ultrabook\b": "Laptops & Ultrabooks",
    r"\binverter|battery|ups|power supply\b": "Inverters",
    r"\bperfume|fragrance|cologne|deodorant\b": "Perfumes",
    r"\bshoe|sandal|sneaker|heel|flipflop\b": "Shoes",
    r"\bbag|backpack|handbag|tote\b": "Bags",
    r"\bskincare|serum|moisturizer|cleanser|toner|cream\b": "Skincare",
    r"\btv|television|led\b": "Televisions",
    r"\bblender|toaster|microwave|kettle|appliance\b": "Small Kitchen Appliances",
    r"\bjean|shirt|dress|trouser|fashion|top|clothing\b": "Fashion",
    r"\bbaby|kid|children\b": "Baby & Kids",
    r"\bfitness|gym|dumbbell|treadmill|exercise|workout\b": "Sport & Fitness",
    r"\bshampoo|conditioner|hair\b": "Haircare",
    r"\bwatch|smartwatch\b": "Wearables",
    r"\bspeaker|earbud|soundbar|headphone\b": "Audio & Wearables"
}

# Function to infer category
def infer_category(text):
    if pd.isna(text):
        return None
    text = text.lower()
    for pattern, category in category_map.items():
        if re.search(pattern, text):
            return category
    return None

# Apply inference to missing categories
missing_mask = df["category_name"].isna()
df.loc[missing_mask, "inferred_category"] = (
    df.loc[missing_mask, "name"].fillna("") + " " +
    df.loc[missing_mask, "description"].fillna("")
).apply(infer_category)

# Fill missing categories
df["category_final"] = df["category_name"]
df.loc[df["category_final"].isna(), "category_final"] = df["inferred_category"]
df["category_final"].fillna("Unknown", inplace=True)

# Summary
filled_count = df["inferred_category"].notna().sum()
still_missing = (df["category_final"] == "Unknown").sum()

print(f"✅ Categories inferred for {filled_count} products.")
print(f"❌ Still Unknown: {still_missing} products.")
print(f"🎯 Total coverage achieved: {round((len(df) - still_missing) / len(df) * 100, 2)}%")

# Save output
df.to_csv("products_with_inferred_categories.csv", index=False)
print("💾 Saved updated dataset as products_with_inferred_categories.csv")

# Optional preview
print(df[["name", "category_name", "inferred_category", "category_final"]].head(15))
