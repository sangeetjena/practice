
analytical functions:
============================
SUM(salary) OVER (PARTITION BY id ORDER BY month RANGE BETWEEN 2 PRECEDING AND CURRENT ROW) AS Salary
