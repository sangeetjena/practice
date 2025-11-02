Convert Rows to Columns (Sales by Quarter)
===========================================
``` sql

-- Given this sales data, pivot it to show quarters as columns
-- Input table: sales (product, quarter, sales_amount)
-- Expected output: product, Q1, Q2, Q3, Q4

-- Method 1: Using CASE statements (works in all databases)
SELECT 
    product,
    SUM(CASE WHEN quarter = 'Q1' THEN sales_amount ELSE 0 END) AS Q1,
    SUM(CASE WHEN quarter = 'Q2' THEN sales_amount ELSE 0 END) AS Q2,
    SUM(CASE WHEN quarter = 'Q3' THEN sales_amount ELSE 0 END) AS Q3,
    SUM(CASE WHEN quarter = 'Q4' THEN sales_amount ELSE 0 END) AS Q4
FROM sales
GROUP BY product;

-- Method 2: Using PIVOT operator (SQL Server, Oracle)
SELECT product, Q1, Q2, Q3, Q4
FROM (
    SELECT product, quarter, sales_amount 
    FROM sales
) AS source_table
PIVOT (
    SUM(sales_amount) 
    FOR quarter IN (Q1, Q2, Q3, Q4)
) AS pivot_table;
```

Unpivot Questions: Convert Columns Back to Rows
===============================================

``` sql
-- Given a pivoted table, convert it back to normalized form
-- Input: product, Q1, Q2, Q3, Q4
-- Output: product, quarter, sales_amount

-- Method 1: Using UNION ALL
SELECT product, 'Q1' AS quarter, Q1 AS sales_amount FROM sales_pivot WHERE Q1 IS NOT NULL
UNION ALL
SELECT product, 'Q2' AS quarter, Q2 AS sales_amount FROM sales_pivot WHERE Q2 IS NOT NULL
UNION ALL
SELECT product, 'Q3' AS quarter, Q3 AS sales_amount FROM sales_pivot WHERE Q3 IS NOT NULL
UNION ALL
SELECT product, 'Q4' AS quarter, Q4 AS sales_amount FROM sales_pivot WHERE Q4 IS NOT NULL;

-- Method 2: Using UNPIVOT operator (SQL Server)
SELECT product, quarter, sales_amount
FROM sales_pivot
UNPIVOT (
    sales_amount FOR quarter IN (Q1, Q2, Q3, Q4)
) AS unpivot_table;
```

Convert string charactor to rows 
=================================
``` sql
convert "sangeet" -> s
                     a
                     n.....

WITH RECURSIVE chars AS (
  SELECT 1 AS pos, SUBSTRING('sangeet', 1, 1) AS ch
  UNION ALL
  SELECT pos + 1, SUBSTRING('sangeet', pos + 1, 1)
  FROM chars
  WHERE pos + 1 <= CHAR_LENGTH('sangeet')
)
SELECT ch
FROM chars;

```
convert string to columns
==========================
``` sql
similar to able, 1st convert string to row, then unpivot it
WITH RECURSIVE chars AS (
  SELECT 1 AS pos, SUBSTRING('sangeet', 1, 1) AS ch
  UNION ALL
  SELECT pos + 1, SUBSTRING('sangeet', pos + 1, 1)
  FROM chars
  WHERE pos + 1 <= CHAR_LENGTH('sangeet')
)
SELECT 
  MAX(CASE WHEN pos = 1 THEN ch END) AS c1,
  MAX(CASE WHEN pos = 2 THEN ch END) AS c2,
  MAX(CASE WHEN pos = 3 THEN ch END) AS c3,
  MAX(CASE WHEN pos = 4 THEN ch END) AS c4,
  MAX(CASE WHEN pos = 5 THEN ch END) AS c5,
  MAX(CASE WHEN pos = 6 THEN ch END) AS c6,
  MAX(CASE WHEN pos = 7 THEN ch END) AS c7
FROM chars;


` OR

WITH chars AS (
  SELECT 1 AS pos, SUBSTRING('sangeet', 1, 1) AS ch
  UNION ALL
  SELECT pos + 1, SUBSTRING('sangeet', pos + 1, 1)
  FROM chars
  WHERE pos + 1 <= LEN('sangeet')
)
SELECT [1] AS c1, [2] AS c2, [3] AS c3, [4] AS c4, [5] AS c5, [6] AS c6, [7] AS c7
FROM (
    SELECT pos, ch
    FROM chars
) AS src
PIVOT (
    MAX(ch) FOR pos IN ([1],[2],[3],[4],[5],[6],[7])
) AS p;
```

Pivot with Date Ranges
======================

``` sql
-- Pivot monthly sales data by product for the last 12 months
-- Handle dynamic date columns

WITH monthly_sales AS (
    SELECT 
        product,
        FORMAT(sale_date, 'yyyy-MM') as month_year,
        sales_amount
    FROM sales
    WHERE sale_date >= DATEADD(MONTH, -12, GETDATE())
)
SELECT 
    product,
    SUM(CASE WHEN month_year = '2025-01' THEN sales_amount END) AS "2025-01",
    SUM(CASE WHEN month_year = '2025-02' THEN sales_amount END) AS "2025-02",
    -- ... continue for all 12 months
    SUM(CASE WHEN month_year = '2025-12' THEN sales_amount END) AS "2025-12"
FROM monthly_sales
GROUP BY product;
```
