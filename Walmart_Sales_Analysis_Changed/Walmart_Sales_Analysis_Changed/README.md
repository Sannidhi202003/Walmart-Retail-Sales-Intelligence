# 🛒 Walmart Retail Sales Intelligence

A refactored end-to-end data analysis project uncovering business insights from Walmart's multi-branch transaction data using Python, SQL, and interactive dashboards.

---

## 📁 Project Structure

```
Walmart_Sales_Analysis_Changed/
├── data/
│   └── walmart_transactions.json       # Raw transaction dataset (9,969 records)
├── src/
│   └── retail_sales_engine.py          # Python data processing & analysis pipeline
├── sql_queries/
│   └── retail_insights_queries.sql     # 10 business insight SQL queries + bonus
├── dashboard/
│   └── retail_intelligence_hub.html    # Interactive Power BI-style dashboard
├── models/                             # Auto-generated CSV summaries (after running src)
├── notebooks/                          # Jupyter notebooks (optional exploration)
└── README.md
```

---

## 📊 Dashboard Features

Open `dashboard/retail_intelligence_hub.html` in any browser, click **Load Data (JSON)** and select `data/walmart_transactions.json`.

| Chart | Type | Description |
|---|---|---|
| KPI Strip | Cards | Revenue, Transactions, Avg Rating, Items Sold, Avg Ticket |
| Revenue by Category | Horizontal Bar | Colour-gradient ranked bar chart |
| Payment Method Split | Donut | Credit Card / Ewallet / Cash breakdown |
| Sales by Day Shift | Polar/Radar | Morning / Afternoon / Evening comparison |
| Daily Revenue Trend | Area + Line | Daily sales with 7-day rolling average overlay |
| Hourly Traffic | Bar Heatmap | Transactions by hour of day |
| Branch Bubble Chart | Bubble Scatter | Revenue vs Profit, sized by transaction count |
| Rating by Category | Box Plot | Distribution with mean & std deviation |
| Top Cities | Treemap | Revenue-weighted city breakdown |
| Monthly Heatmap | Heatmap | Category × Month revenue intensity grid |

---

## 🗃️ SQL Business Questions Answered

1. **Payment Method Analysis** — Transaction count & revenue per payment type  
2. **Top-Rated Category Per Branch** — Customer satisfaction leaders  
3. **Busiest Day Per Branch** — Peak trading days for staffing  
4. **Highest Revenue Category** — Best-performing product segment  
5. **Peak Transaction Hours** — Optimal promotional timing  
6. **City-Level Performance** — Average spend by location  
7. **Stock Demand Ranking** — Units sold per category for restocking  
8. **Dominant Payment Per Branch** — Location-specific payment preferences  
9. **Year-Over-Year Revenue Decline** — Branches losing revenue (2022 vs 2023)  
10. **Sales Shift Distribution** — Morning / Afternoon / Evening patterns  
11. **Bonus: Profit Margin by Branch & Category**

---

## ⚙️ Setup & Installation

### Requirements
- Python 3.8+
- PostgreSQL or MySQL

### Python Dependencies
```bash
pip install pandas numpy sqlalchemy psycopg2 mysql-connector-python
```

### Run the Analysis Pipeline
```bash
cd src/
python retail_sales_engine.py
```
This outputs CSV summaries to the `models/` folder.

### Run the Dashboard
Simply open in browser:
```
dashboard/retail_intelligence_hub.html
```
Then load `data/walmart_transactions.json` using the file picker.

---

## 📌 Dataset

- **Source:** Kaggle — Walmart 10K Sales Dataset  
- **Records:** 9,969 transactions  
- **Fields:** Invoice ID, Branch, City, Category, Unit Price, Quantity, Date, Time, Payment Method, Rating, Profit Margin, Total

---

## 💡 Key Insights

- **Home & Lifestyle** and **Fashion Accessories** are the top revenue categories
- **Ewallet** and **Credit Card** dominate as payment preferences
- **Afternoon shift** (12–18h) sees the highest transaction volume
- Branch revenue shows YoY variation worth monitoring for underperforming locations

---

## 🔮 Future Enhancements

- Real-time data pipeline with automated ingestion
- Machine learning for demand forecasting
- Customer segmentation using clustering
- Integration with live Power BI / Tableau reports
