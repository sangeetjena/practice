"""
https://leetcode.com/problems/managers-with-at-least-5-direct-reports/description/?envType=study-plan-v2&envId=top-sql-50
  
Table: Employee

+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| id          | int     |
| name        | varchar |
| department  | varchar |
| managerId   | int     |
+-------------+---------+
id is the primary key (column with unique values) for this table.
Each row of this table indicates the name of an employee, their department, and the id of their manager.
If managerId is null, then the employee does not have a manager.
No employee will be the manager of themself.
 

Write a solution to find managers with at least five direct reports.

Return the result table in any order.

The result format is in the following example.


"""

# Write your MySQL query statement below
with x as (
    select managerid
    from employee
    group by managerid
    having count(1)>=5
)
select name 
from employee e
join
x
on(e.id = x.managerid)


"""
######################################
###################Pandas:###################
######################################
"""
import pandas as pd

# Sample data
data = {
    'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Edward', 'Fay', 'Grace', 'Hannah', 'Ivy', 'Jack'],
    'managerid': [None, 1, 1, 2, 2, 3, 3, 4, 4, 5]
}

# Create DataFrame
df = pd.DataFrame(data)

# Group by managerid and filter those having more than or equal to 5 direct reportees
manager_counts = df.groupby('managerid').size().reset_index(name='count')
managers_with_5_or_more_reportees = manager_counts[manager_counts['count'] >= 5]

# Join back to get the names of these managers
result = df[df['id'].isin(managers_with_5_or_more_reportees['managerid'])][['name']]
print(result)
