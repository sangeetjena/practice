"""
https://leetcode.com/problems/friend-requests-ii-who-has-the-most-friends/description/
  
"""
# Write your MySQL query statement below
with uniqueid as(
    select  requester_id as userid from requestaccepted
    union all
    select  accepter_id as userid from requestaccepted
),
x as (
select userid, count(*) as num, rank()over(order by count(*) desc) as rnk
from uniqueid
group by userid
)
select userid as id,num  from x where rnk=1
