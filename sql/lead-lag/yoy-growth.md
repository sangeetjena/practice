```
https://datalemur.com/questions/yoy-growth-rate

This is the same question as problem #32 in the SQL Chapter of Ace the Data Science Interview!

Assume you're given a table containing information about Wayfair user transactions for different products. Write a query to calculate the year-on-year growth rate for the total spend of each product, grouping the results by product ID.

The output should include the year in ascending order, product ID, current year's spend, previous year's spend and year-on-year growth percentage, rounded to 2 decimal places.

```
<img width="836" height="920" alt="image" src="https://github.com/user-attachments/assets/a1354ae3-d773-459c-a68d-946a1a0fdb73" />


``` sql
WITH product_sales_yr AS (
    SELECT 
        EXTRACT(YEAR FROM transaction_date) AS yr,
        product_id,
        SUM(spend) AS spend
    FROM user_transactions
    GROUP BY yr, product_id
),

prev_year AS (
    SELECT 
        product_id,
        yr,
        spend,
        LAG(spend, 1) OVER (PARTITION BY product_id ORDER BY yr ASC) AS previous_spend
    FROM product_sales_yr
)

SELECT 
    yr AS year,
    product_id,
    spend AS curr_year_spend,
    previous_spend AS prev_year_spend,
    ROUND(
        CASE 
            WHEN previous_spend IS NULL THEN NULL
            ELSE ((spend - previous_spend) / previous_spend::FL

```
