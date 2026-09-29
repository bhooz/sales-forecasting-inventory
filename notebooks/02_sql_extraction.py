import os
import sqlite3
import pandas as pd

# Define paths dynamically relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "inventory.db"))
sql_path = os.path.normpath(os.path.join(BASE_DIR, "..", "sql", "aggregate_sales.sql"))
output_csv_path = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "aggregated_sales.csv"))

print("Connecting to database at:", db_path)
conn = sqlite3.connect(db_path)

# Read SQL query from file
with open(sql_path, "r") as file:
    sql_query = file.read()

# Execute query and load into DataFrame
aggregated_df = pd.read_sql_query(sql_query, conn)
conn.close()

# Convert sales_date to datetime format (handles multiple formats safely)
aggregated_df['sales_date'] = pd.to_datetime(aggregated_df['sales_date'], format='mixed')

# Export aggregated data to CSV for Python ML modeling
aggregated_df.to_csv(output_csv_path, index=False)

print("\nSuccess! Aggregated dataset exported to:", output_csv_path)
print("Shape:", aggregated_df.shape)
print("\nFirst 5 rows:")
print(aggregated_df.head())