-- ============================================================
-- FILE: retail_insights_queries.sql
-- PROJECT: Walmart Retail Sales Intelligence
-- DESCRIPTION: Business insight queries for sales, performance,
--              customer behaviour and revenue analysis
-- ============================================================

-- Preview full dataset
SELECT * FROM retail_sales_data;

-- Drop existing table if rebuilding
DROP TABLE IF EXISTS retail_sales_data;

-- Total record count
SELECT COUNT(*) AS total_transactions FROM retail_sales_data;

-- ── QUERY 1: Payment Method Breakdown ──────────────────────────
-- Goal: Identify how customers prefer to pay and transaction volume per method
SELECT
    payment_method                        AS payment_type,
    COUNT(*)                              AS total_transactions,
    SUM(quantity)                         AS total_items_sold,
    ROUND(SUM(total)::NUMERIC, 2)         AS total_revenue
FROM retail_sales_data
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- ── QUERY 2: Top-Rated Product Category Per Branch ─────────────
-- Goal: Find which category customers rate highest in each store branch
SELECT branch, category, avg_rating, branch_rank
FROM (
    SELECT
        branch,
        category,
        ROUND(AVG(rating)::NUMERIC, 2)  AS avg_rating,
        RANK() OVER (
            PARTITION BY branch
            ORDER BY AVG(rating) DESC
        )                               AS branch_rank
    FROM retail_sales_data
    GROUP BY branch, category
) ranked_categories
WHERE branch_rank = 1
ORDER BY branch;

-- ── QUERY 3: Busiest Trading Day Per Branch ─────────────────────
-- Goal: Determine peak day of week per branch for staffing decisions
SELECT branch, day_name, transaction_count
FROM (
    SELECT
        branch,
        TO_CHAR(TO_DATE(date, 'DD/MM/YY'), 'DAY') AS day_name,
        COUNT(*)                                    AS transaction_count,
        RANK() OVER (
            PARTITION BY branch
            ORDER BY COUNT(*) DESC
        )                                           AS day_rank
    FROM retail_sales_data
    GROUP BY branch, day_name
) daily_traffic
WHERE day_rank = 1
ORDER BY branch;

-- ── QUERY 4: Highest Revenue-Generating Category ───────────────
-- Goal: Identify the single best-performing product category by revenue
SELECT
    category                          AS product_category,
    ROUND(SUM(total)::NUMERIC, 2)     AS total_revenue,
    COUNT(*)                          AS num_transactions,
    ROUND(AVG(total)::NUMERIC, 2)     AS avg_transaction_value
FROM retail_sales_data
GROUP BY product_category
ORDER BY total_revenue DESC
LIMIT 1;

-- ── QUERY 5: Peak Transaction Hours ────────────────────────────
-- Goal: Find the hour of the day when most transactions occur
SELECT
    CAST(SPLIT_PART(time, ':', 1) AS INTEGER)  AS hour_of_day,
    COUNT(*)                                    AS transaction_count,
    ROUND(SUM(total)::NUMERIC, 2)               AS hourly_revenue
FROM retail_sales_data
GROUP BY hour_of_day
ORDER BY transaction_count DESC
LIMIT 5;

-- ── QUERY 6: City-Level Average Transaction Value ───────────────
-- Goal: Discover which cities drive the highest average spend
SELECT
    city,
    COUNT(*)                              AS num_transactions,
    ROUND(AVG(total)::NUMERIC, 2)         AS avg_transaction_value,
    ROUND(SUM(total)::NUMERIC, 2)         AS total_city_revenue
FROM retail_sales_data
GROUP BY city
ORDER BY avg_transaction_value DESC
LIMIT 10;

-- ── QUERY 7: Category Stock Demand Ranking ─────────────────────
-- Goal: Rank categories by total units sold to guide restocking
SELECT
    category,
    SUM(quantity)                         AS total_units_sold,
    ROUND(AVG(unit_price)::NUMERIC, 2)    AS avg_unit_price,
    COUNT(*)                              AS num_transactions
FROM retail_sales_data
GROUP BY category
ORDER BY total_units_sold DESC;

-- ── QUERY 8: Dominant Payment Method Per Branch ────────────────
-- Goal: Understand payment preference at each store location
WITH payment_ranked AS (
    SELECT
        branch,
        payment_method,
        COUNT(*)  AS transaction_count,
        RANK() OVER (
            PARTITION BY branch
            ORDER BY COUNT(*) DESC
        )         AS preference_rank
    FROM retail_sales_data
    GROUP BY branch, payment_method
)
SELECT branch, payment_method, transaction_count
FROM payment_ranked
WHERE preference_rank = 1
ORDER BY branch;

-- ── QUERY 9: Year-Over-Year Revenue Decline By Branch ──────────
-- Goal: Flag branches with falling revenue from 2022 to 2023
WITH revenue_by_year AS (
    SELECT
        branch,
        EXTRACT(YEAR FROM TO_DATE(date, 'DD/MM/YY')) AS sales_year,
        SUM(total)                                    AS annual_revenue
    FROM retail_sales_data
    WHERE EXTRACT(YEAR FROM TO_DATE(date, 'DD/MM/YY')) IN (2022, 2023)
    GROUP BY branch, sales_year
),
prev_year AS (
    SELECT branch, annual_revenue AS revenue_2022
    FROM revenue_by_year WHERE sales_year = 2022
),
curr_year AS (
    SELECT branch, annual_revenue AS revenue_2023
    FROM revenue_by_year WHERE sales_year = 2023
)
SELECT
    p.branch,
    ROUND(p.revenue_2022::NUMERIC, 2)                                   AS revenue_2022,
    ROUND(c.revenue_2023::NUMERIC, 2)                                   AS revenue_2023,
    ROUND(((p.revenue_2022 - c.revenue_2023) / p.revenue_2022 * 100)::NUMERIC, 2) AS pct_decline
FROM prev_year p
JOIN curr_year c ON p.branch = c.branch
WHERE p.revenue_2022 > c.revenue_2023
ORDER BY pct_decline DESC
LIMIT 5;

-- ── QUERY 10: Sales Distribution Across Day Shifts ─────────────
-- Goal: Understand Morning / Afternoon / Evening transaction patterns
SELECT
    branch,
    CASE
        WHEN EXTRACT(HOUR FROM time::TIME) < 12             THEN 'Morning'
        WHEN EXTRACT(HOUR FROM time::TIME) BETWEEN 12 AND 17 THEN 'Afternoon'
        ELSE                                                      'Evening'
    END                         AS day_shift,
    COUNT(*)                    AS transaction_count,
    ROUND(SUM(total)::NUMERIC, 2) AS shift_revenue
FROM retail_sales_data
GROUP BY branch, day_shift
ORDER BY branch, transaction_count DESC;

-- ── BONUS: Profit Margin Analysis By Category & Branch ─────────
SELECT
    branch,
    category,
    ROUND(AVG(profit_margin)::NUMERIC, 4)   AS avg_profit_margin,
    ROUND(SUM(total * profit_margin)::NUMERIC, 2) AS estimated_profit,
    COUNT(*)                                 AS transactions
FROM retail_sales_data
GROUP BY branch, category
ORDER BY estimated_profit DESC
LIMIT 20;
