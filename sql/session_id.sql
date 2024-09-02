"""
https://www.hackerrank.com/challenges/sql-projects/problem?isFullScreen=true
  
Note: similar to session id creation.
"""
with temp as 
(select start_date, end_date, row_number()over(order by start_date asc) as rnk
from projects
),
x as(
select  start_date, end_date, date_sub(end_date,interval rnk day) as grp
    from temp
)
select min(start_date), max(end_date)
from x 
group by grp
order by count(*) asc
