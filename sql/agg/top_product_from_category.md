```
Assume you're given a table containing data on Amazon customers and their spending on products in different category,
 write a query to identify the top two highest-grossing products within each category in the year 2022.
The output should include the category, product, and total spend.

```
<img width="803" height="903" alt="image" src="https://github.com/user-attachments/assets/580a858b-3815-4404-b6ca-e1faa60f9e43" />


``` sql
with agg_sales as (
select category, product, sum(spend) as total_cost
from product_spend 
where extract( YEAR from transaction_date) = '2022'
group by category, product
),
x as (select category,product, total_cost, rank()over(PARTITION by category order by total_cost desc) as rnk
from 
agg_sales)
select category,product, total_cost
from x
where rnk <3

```
