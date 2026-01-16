<img width="792" height="616" alt="image" src="https://github.com/user-attachments/assets/7cb021d9-630e-4cfd-b1de-b5b93e5b75a5" />

```
https://leetcode.com/problems/report-contiguous-dates/description/?envType=study-plan-v2&envId=premium-sql-50


A system is running one task every day. Every task is independent of the previous tasks. The tasks can fail or succeed.

Write a solution to report the period_state for each continuous interval of days in the period from 2019-01-01 to 2019-12-31.

period_state is 'failed' if tasks in this interval failed or 'succeeded' if tasks in this interval succeeded. Interval of days are retrieved as start_date and end_date.

Return the result table ordered by start_date.

The result format is in the following example.




```

<img width="792" height="840" alt="image" src="https://github.com/user-attachments/assets/52343792-0d79-4a4e-b09c-a2402dae7bcb" />


``` sql
# Write your MySQL query statement below
with temp as
(
    select fail_date as dt, 'failed' status
    from failed
    union
    select success_Date as dt, 'succeeded' status
    from
    succeeded
),
rnk as (
select *, row_number()over(partition by status order by dt asc) as rnk
from temp
where dt between '2019-01-01' and '2019-12-31'
),
grp as (
select concat(date_sub(dt ,interval rnk day), status) as grp, dt, status
from rnk 

)
select max(status) as period_state, min(dt) as start_date,max(dt) as end_date
from grp 
group by grp
order by dt asc
```
