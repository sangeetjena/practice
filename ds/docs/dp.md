# Dynamic Programming:
Dynamic programming is a programming pardigm which deals with breaking the larger problem into smaller problem. and store the result of smaller problem and reuse the results if the same problem occure again.

## how we will idnentify if the problem is needed DP approach or not ?
1- if a big problem can be broken into smaller problem and the smaller problem is repeating 
2-  find all possible combination.

https://www.youtube.com/watch?v=mBNrRy2_hVs&t=42s
0-1 napsack:
==============
```
A knapsack is defined as a bag carried by hikers or soldiers for carrying food, clothes, and other belongings. The Knapsack problem, as the name suggests, is the problem faced by a person who has a knapsack with a limited capacity and wants to carry the most valuable items. In other words, we are given items, each having a specific weight and a value, and a knapsack with a maximum capacity. Our job is to put as many items as possible in the knapsack such that the cumulative weight of the items doesn't exceed the knapsack's capacity, and the cumulative value of the items in the knapsack is maximized.

The 0/1 Knapsack is a special case of the Knapsack problem where item selection has some constraints. In general, the following restrictions are applied:
A maximum of one item can be selected of each kind, that is, the number of items of each kind in the knapsack is either zero or one.
We can't take a fraction of an item, that is, we either have to take the complete item or leave it.

```
