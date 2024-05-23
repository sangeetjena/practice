"""
https://www.hackerrank.com/challenges/symmetric-pairs/problem?isFullScreen=true
"""

with tmp as (
select 
    x,
    y, 
    rank()over(order by x desc) as rnk
from Functions
)
select 
distinct f1.x,
f1.y
from 
tmp f1
join
tmp f2
on (f1.x = f2.y and f1.y = f2.x)
where f1.rnk != f2.rnk
and f1.x<=f1.y
order by f1.x asc;
