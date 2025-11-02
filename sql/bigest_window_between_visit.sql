"""
https://leetcode.com/problems/biggest-window-between-visits/description/

Example 1:
Input: 
UserVisits table:
+---------+------------+
| user_id | visit_date |
+---------+------------+
| 1       | 2020-11-28 |
| 1       | 2020-10-20 |
| 1       | 2020-12-3  |
| 2       | 2020-10-5  |
| 2       | 2020-12-9  |
| 3       | 2020-11-11 |
+---------+------------+
Output: 
+---------+---------------+
| user_id | biggest_window|
+---------+---------------+
| 1       | 39            |
| 2       | 65            |
| 3       | 51            |
+---------+---------------+

"""

# Write your MySQL query statement below
with visit as (
    select user_id, 
        visit_date,
        lead(visit_date, 1, '2021-1-1')over(partition by user_id order by visit_date asc)as ld,             
        datediff(lead(visit_date, 1, '2021-1-1')over(partition by user_id order by visit_date asc), visit_date) as max_diff
    from userVisits 
),
rnk as (
    select *, rank()over(partition by user_id order by max_diff desc) as rk
    from visit
)
select distinct user_id,max_diff as biggest_window  from rnk
where rk=1
