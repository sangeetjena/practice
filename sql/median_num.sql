"""
https://leetcode.com/problems/find-median-given-frequency-of-numbers/
  
Note: using recursive query

Example 1:

Input: 
Numbers table:
+-----+-----------+
| num | frequency |
+-----+-----------+
| 0   | 7         |
| 1   | 1         |
| 2   | 3         |
| 3   | 1         |
+-----+-----------+
Output: 
+--------+
| median |
+--------+
| 0.0    |
+--------+
Explanation: 
If we decompress the Numbers table, we will get [0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 3], so the median is (0 + 0) / 2 = 0.
"""
# Write your MySQL query statement below
with recursive x as (
    select *, 1 as cnt from numbers
    union all
    select num, frequency, cnt+1 as cnt from x where cnt< x.frequency
),
y as (
    select num, count(*)over() as totalcnt, row_number()over(order by num asc) rn from x order by num,frequency
)
select avg(num) as median from y 
where rn>=totalcnt/2 and rn<=totalcnt/2+1
