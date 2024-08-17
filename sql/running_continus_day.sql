"""
https://leetcode.com/problems/report-contiguous-dates/description/

A system is running one task every day. Every task is independent of the previous tasks. The tasks can fail or succeed.

Write a solution to report the period_state for each continuous interval of days in the period from 2019-01-01 to 2019-12-31.

period_state is 'failed' if tasks in this interval failed or 'succeeded' if tasks in this interval succeeded. Interval of days are retrieved as start_date and end_date.

Return the result table ordered by start_date.

The result format is in the following example.

 

Example 1:

Input: 
Failed table:
+-------------------+
| fail_date         |
+-------------------+
| 2018-12-28        |
| 2018-12-29        |
| 2019-01-04        |
| 2019-01-05        |
+-------------------+
Succeeded table:
+-------------------+
| success_date      |
+-------------------+
| 2018-12-30        |
| 2018-12-31        |
| 2019-01-01        |
| 2019-01-02        |
| 2019-01-03        |
| 2019-01-06        |
+-------------------+
Output: 
+--------------+--------------+--------------+
| period_state | start_date   | end_date     |
+--------------+--------------+--------------+
| succeeded    | 2019-01-01   | 2019-01-03   |
| failed       | 2019-01-04   | 2019-01-05   |
| succeeded    | 2019-01-06   | 2019-01-06   |
+--------------+--------------+--------------+
"""

# Write your MySQL query statement below
with x as (
    select fail_date as dt, "failed" as period_state, rank()over(order by fail_date asc) rnk
    from failed 
    where fail_date between '2019-01-01' and '2019-12-31'
    union
    select success_date as dt, "succeeded" as period_state, rank()over(order by success_date asc) rnk
    from 
    succeeded
    where success_date between '2019-01-01' and '2019-12-31'
)
select max(period_state) as period_state, min(dt) as start_date, max(dt) as end_date
from x
group by date_sub(dt, interval rnk day), period_state
order by dt asc
