import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

# 1. Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_csv = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "aggregated_sales.csv"))
output_forecast_csv = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "forecasted_inventory_data.csv"))

# 2. Load dataset
df = pd.read_csv(input_csv)
df['sales_date'] = pd.to_datetime(df['sales_date'])

# Aggregate sales to WEEKLY level per category
df.set_index('sales_date', inplace=True)
weekly_sales = (
    df.groupby(['category', pd.Grouper(freq='W-MON')])['total_sales']
    .sum()
    .reset_index()
)

# 3. Feature Engineering for Weekly Data
weekly_sales['year'] = weekly_sales['sales_date'].dt.year
weekly_sales['month'] = weekly_sales['sales_date'].dt.month
weekly_sales['week_of_year'] = weekly_sales['sales_date'].dt.isocalendar().week.astype(int)
weekly_sales['quarter'] = weekly_sales['sales_date'].dt.quarter

# Encode Category
weekly_sales['category_code'] = weekly_sales['category'].astype('category').cat.codes

# Create Weekly Lag features (sales 1 week ago and 4 weeks ago)
weekly_sales = weekly_sales.sort_values(['category', 'sales_date'])
weekly_sales['lag_1_week'] = weekly_sales.groupby('category')['total_sales'].shift(1)
weekly_sales['lag_4_week'] = weekly_sales.groupby('category')['total_sales'].shift(4)

# Drop missing values from lag creation
data_ml = weekly_sales.dropna().copy()

# 4. Train / Test Split (Train on historical, Test on final 12 weeks)
max_date = data_ml['sales_date'].max()
split_date = max_date - pd.Timedelta(weeks=12)

train = data_ml[data_ml['sales_date'] <= split_date]
test = data_ml[data_ml['sales_date'] > split_date].copy()

features = ['category_code', 'year', 'month', 'week_of_year', 'quarter', 'lag_1_week', 'lag_4_week']
target = 'total_sales'

X_train, y_train = train[features], train[target]
X_test, y_test = test[features], test[target]

# 5. Model Training (XGBoost Regressor)
model = xgb.XGBRegressor(n_estimators=150, learning_rate=0.03, max_depth=4, random_state=42)
model.fit(X_train, y_train)

# Make Predictions
test['forecasted_sales'] = model.predict(X_test)
test['forecasted_sales'] = test['forecasted_sales'].clip(lower=0)

# Evaluate Accuracy
rmse = np.sqrt(mean_squared_error(y_test, test['forecasted_sales']))
# Exclude zero values to protect MAPE
non_zero_mask = y_test > 0
mape = mean_absolute_percentage_error(y_test[non_zero_mask], test.loc[non_zero_mask, 'forecasted_sales']) * 100

print(f"--- Model Evaluation (Weekly Forecast) ---")
print(f"RMSE: ${rmse:.2f}")
print(f"MAPE: {mape:.2f}% (Forecast Accuracy: {max(0, 100 - mape):.2f}%)")

# 6. Inventory Parameters (Weekly Basis)
LEAD_TIME_WEEKS = 1  # 1 week lead time
Z_SCORE = 1.65        # 95% service level

inventory_summary = []
for cat in test['category'].unique():
    cat_data = test[test['category'] == cat]
    
    avg_weekly_demand = cat_data['forecasted_sales'].mean()
    std_weekly_demand = cat_data['forecasted_sales'].std()
    
    safety_stock = Z_SCORE * std_weekly_demand * np.sqrt(LEAD_TIME_WEEKS)
    reorder_point = (avg_weekly_demand * LEAD_TIME_WEEKS) + safety_stock
    
    inventory_summary.append({
        'category': cat,
        'avg_weekly_demand': round(avg_weekly_demand, 2),
        'safety_stock_units': round(safety_stock, 2),
        'reorder_point_units': round(reorder_point, 2)
    })

inv_df = pd.DataFrame(inventory_summary)
print("\n--- Inventory Decision Parameters (Weekly) ---")
print(inv_df)

# Merge back and save CSV for Power BI
final_df = test.merge(inv_df, on='category', how='left')
final_df.to_csv(output_forecast_csv, index=False)
print(f"\nCleaned dataset ready for Power BI exported to: {output_forecast_csv}")