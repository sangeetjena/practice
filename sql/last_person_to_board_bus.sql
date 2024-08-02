"""
https://leetcode.com/problems/last-person-to-fit-in-the-bus/description/?envType=study-plan-v2&envId=top-sql-50

1204. Last Person to Fit in the Bus

"""

with tmp_queue as (
     select turn,
     person_name,
    sum(weight)over(order by turn asc rows between unbounded preceding and current row ) as total_weight
    from queue
),
y as (select  rank()over(order by total_weight desc) rnk, person_name
from tmp_queue
where total_weight <=1000
)
select person_name from y where rnk=1


