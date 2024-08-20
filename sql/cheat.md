
analytical functions:
============================
```SUM(salary) OVER (PARTITION BY id ORDER BY month RANGE BETWEEN 2 PRECEDING AND CURRENT ROW) AS Salary
  sum(weight)over(order by turn asc rows between unbounded preceding and current row )
  rank()over(order by total_weight desc)
```



Date format:
===========================
```DATE_FORMAT(created_at, '%Y-%m') = '2020-02'
   date_sub(dt, interval rnk day)
```

Recursive query:
===========================

```
wtih [RECURSIVE] cte as (
  select [ base query]
    union all
  recursive query from cte [with condition to break the loop]
)
select from cte
```

##### ex: print numbers from 1 to 10:
```
with recursive cte as (
  select 1 as num
    union all
  select num +1
    from cte where num <10
  )
select * form cte
```

##### Ex: print employee in level (1,4,5)
```
with recursive cte as (
  select empid, "" as managername, empname, 1 as level
  from emp
  where managerid is null

  union all

  select c.empid, c.empname as managername, e.empname, level+1 as level
  from
    cte c
  join emp e
  on (e.managerid = c.empid)
)
select * from cte where level in (1,4,5)

```
