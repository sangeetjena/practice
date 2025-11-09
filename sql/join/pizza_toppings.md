```
You’re a consultant for a major pizza chain that will be running a promotion where all 3-topping pizzas will be sold
for a fixed price, and are trying to understand the costs involved.

Given a list of pizza toppings, consider all the possible 3-topping pizzas, and print out the total cost of those 3
toppings. Sort the results with the highest total cost on the top followed by pizza toppings in ascending order.

Break ties by listing the ingredients in alphabetical order, starting from the first ingredient,
followed by the second and third.

P.S. Be careful with the spacing (or lack of) between each ingredient. Refer to our Example Output.

Notes:

Do not display pizzas where a topping is repeated. For example, ‘Pepperoni,Pepperoni,Onion Pizza’.
Ingredients must be listed in alphabetical order. For example, 'Chicken,Onions,Sausage'. 'Onion,Sausage,Chicken'
is not acceptable.


```
<img width="798" height="819" alt="image" src="https://github.com/user-attachments/assets/d6383cd7-6d01-48ff-9427-b6485bc27545" />


``` sql
with x as (
select topping_name, ingredient_cost, rank()over(order by topping_name desc) as rn
from 
pizza_toppings
)
, y as (
select concat(a.topping_name,',', b.topping_name,',', c.topping_name)as pizza,
 (a.ingredient_cost +b.ingredient_cost +c.ingredient_cost) as total_cost
from 
x a
join x b
on(a.rn>b.rn)
join x c
on (a.rn>c.rn and b.rn>c.rn)
)
select * from y 
order by total_cost desc, pizza asc;

```
