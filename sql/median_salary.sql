"""
https://leetcode.com/problems/median-employee-salary/description/

"""
# Write your MySQL query statement below
with midian as (
    select 
        id, company, salary, count(*)over(partition by company) as cnt, row_number()over(partition by company order by salary asc) as mid
    from 
        employee
)
select id, company, salary
from midian
where mid>=cnt/2 and mid<=cnt/2+1
