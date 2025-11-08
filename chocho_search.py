import pandas as pd
from sqlalchemy import create_engine


# Database credentials
user="chocho_analyst"
password="ChoCho2025!Analytics#ReadOnly"
host="ep-polished-night-aev76ljb.c-2.us-east-2.aws.neon.tech"
port=5432
database="neondb"
    

# Create a connection string
engine = create_engine("postgresql+psycopg2://chocho_analyst:ChoCho2025!Analytics#ReadOnly@ep-polished-night-aev76ljb.c-2.us-east-2.aws.neon.tech:5432/neondb")

# Example query to fetch data from a specific table
query = "SELECT * FROM products LIMIT 10;"
df = pd.read_sql_query(query, engine)
print(df)

#see column names
print(df.columns)

# see data types and non-null counts
print(df.info())

# Display the first 20 rows of the DataFrame
print(df.head(20))

# See unique categories
query = """
SELECT 
    p.id,
    p.name,
    p.description,
    p.price,
    p.stock_quantity,
    c.name AS category_name
FROM products p
LEFT JOIN categories c
ON p.category_id = c.id
LIMIT 20;
"""

df = pd.read_sql_query(query, engine)
print(df.head(20))

# See unique categories
print(df['category_name'].unique())
