
analytical functions:
============================
SUM(salary) OVER (PARTITION BY id ORDER BY month RANGE BETWEEN 2 PRECEDING AND CURRENT ROW) AS Salary
sum(weight)over(order by turn asc rows between unbounded preceding and current row )
rank()over(order by total_weight desc)




Date format:
===========================
DATE_FORMAT(created_at, '%Y-%m') = '2020-02'
date_sub(dt, interval rnk day)
