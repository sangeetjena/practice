"""
  https://leetcode.com/problems/product-sales-analysis-iv/description/
  
Table: Sales

+-------------+-------+
| Column Name | Type  |
+-------------+-------+
| sale_id     | int   |
| product_id  | int   |
| user_id     | int   |
| quantity    | int   |
+-------------+-------+
sale_id contains unique values.
product_id is a foreign key (reference column) to Product table.
Each row of this table shows the ID of the product and the quantity purchased by a user.
 

Table: Product

+-------------+------+
| Column Name | Type |
+-------------+------+
| product_id  | int  |
| price       | int  |
+-------------+------+
product_id contains unique values.
Each row of this table indicates the price of each product.
 

Write a solution that reports for each user the product id on which the user spent the most money. In case the same user spent the most money on two or more products, report all of them.

Return the resulting table in any order.

The result format is in the following example.
"""

# Write your MySQL query statement below
with temp as (
    select user_id, product_id, sum(quantity) as quantity
    from sales
    group by user_id, product_id
),
total as (
select 
    s.product_id,s.user_id, s.quantity,s.quantity*p.price amount, rank()over(partition by user_id order by s.quantity*p.price desc) as rnk
from
    temp s
join 
    product p
on( s.product_id =  p.product_id)
)
select user_id, product_id
from total
where rnk=1
