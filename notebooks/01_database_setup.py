import os
import sqlite3
import pandas as pd

# 1. Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "raw_sales.csv"))
db_path = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "inventory.db"))

# 2. Read dataset
df = pd.read_csv(data_path, encoding='ISO-8859-1')
print("Raw Data Loaded Successfully! Shape:", df.shape)

# Clean column names (replace spaces & hyphens with underscores)
df.columns = df.columns.str.replace(' ', '_').str.replace('-', '_').str.lower()

# 3. Connect to SQLite and write table
conn = sqlite3.connect(db_path)
df.to_sql('raw_sales', conn, if_exists='replace', index=False)
conn.close()

print("Data successfully stored in 'inventory.db' under table 'raw_sales'!")