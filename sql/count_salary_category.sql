"""
https://leetcode.com/problems/count-salary-categories/description/?envType=study-plan-v2&envId=top-sql-50

  Table: Accounts

+-------------+------+
| Column Name | Type |
+-------------+------+
| account_id  | int  |
| income      | int  |
+-------------+------+
account_id is the primary key (column with unique values) for this table.
Each row contains information about the monthly income for one bank account.
 

Write a solution to calculate the number of bank accounts for each salary category. The salary categories are:

"Low Salary": All the salaries strictly less than $20000.
"Average Salary": All the salaries in the inclusive range [$20000, $50000].
"High Salary": All the salaries strictly greater than $50000.
The result table must contain all three categories. If there are no accounts in a category, return 0.

Return the result table in any order.

The result format is in the following example.
"""
# Write your MySQL query statement below
with cat as (
    select "High Salary" as category  from dual
    union all
    select "Low Salary" as category from dual
    union all
    select "Average Salary" as category from dual
    
),
tmp as (
    select account_id,
           income, 
           case when income < 20000 then  "Low Salary"
            when income between 20000 and 50000 then "Average Salary"
            when income > 50000 then "High Salary"
           end as category
    from accounts
)
select 
    c.category,
    case when t.category is null then 0
    else count(1)
    end as accounts_count
from cat c
left join tmp t
on (c.category = t.category)
group by c.category
