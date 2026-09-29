# 📊 Retail Sales Forecasting & Inventory Optimization Dashboard

## 📌 Executive Summary
This project delivers an end-to-end data engineering and predictive analytics pipeline designed to solve a core retail supply chain challenge: **balancing stockout risk against excess holding costs**. 

Using historical retail transaction data, the system extracts aggregated trends via SQL, trains an **XGBoost machine learning model** to predict weekly demand, computes safety stock parameters, and presents actionable insights through an interactive **Power BI Executive Dashboard**.

---

## 🛠️ Architecture & Tech Stack
- **Database Storage & Aggregation:** SQLite, SQL
- **Data Processing & ML Pipeline:** Python (`pandas`, `numpy`, `scikit-learn`, `xgboost`)
- **Dashboard & BI Visualization:** Power BI Desktop
- **Environment & Version Control:** Git, VS Code

---

## ⚙️ Project Pipeline

```text
[ Raw Sales CSV ] 
       │
       ▼
[ SQLite Database ] ──( SQL Queries )──► [ Aggregated Weekly Data ]
                                                     │
                                                     ▼
                                          [ XGBoost Forecast Model ]
                                                     │
                                                     ▼
                                         [ Safety Stock & ROP Logic ]
                                                     │
                                                     ▼
                                         [ Power BI Executive Dashboard ]