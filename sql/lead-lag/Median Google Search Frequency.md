
<img width="1113" height="977" alt="image" src="https://github.com/user-attachments/assets/b6fd838b-5d59-4b91-b045-bc4c6d8aca2b" />



``` sql
WITH temp1 AS (
    SELECT 
        searches, 
        SUM(num_users) OVER (ORDER BY searches) AS cum_sum
    FROM search_frequency
),

temp2 AS (
    SELECT 
        searches, 
        cum_sum,
        LAG(cum_sum, 1, 0) OVER (ORDER BY searches) AS prev_cum_sum
    FROM temp1
),

total AS (
    SELECT MAX(cum_sum) AS total_count FROM temp1
)

SELECT round(AVG(searches),1) AS median
FROM temp2, total
WHERE 
    -- odd case
    (total_count % 2 = 1 AND 
     (total_count + 1) / 2 BETWEEN prev_cum_sum + 1 AND cum_sum)
    
    OR
    
    -- even case
    (total_count % 2 = 0 AND 
     (
       total_count / 2 BETWEEN prev_cum_sum + 1 AND cum_sum
       OR
       total_count / 2 + 1 BETWEEN prev_cum_sum + 1 AND cum_sum
     )
    );

```
