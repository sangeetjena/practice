Joins:
============================
```
| A |
|---|
| 1 |
| 2 |
| 3 |

### Table Y
| B |
|---|
| 2 |
| 3 |
| 4 |

| Join Type           | Description                                           | Rows Returned | Notes                 |
| ------------------- | ----------------------------------------------------- | ------------- | --------------------- |
| **INNER JOIN**      | Only rows with matching values in both tables         | 2             | Common join type      |
| **LEFT JOIN**       | All rows from X + matches from Y                      | 3             | `OUTER` optional      |
| **LEFT OUTER JOIN** | Same as LEFT JOIN                                     | 3             | Same result           |
| **CROSS JOIN**      | Cartesian product of X and Y                          | 9             | No join condition     |
| **FULL OUTER JOIN** | All rows from both tables, with NULLs for non-matches | 4             | Combines left + right |

```
analytical functions:
============================
```
  ROWS BETWEEN lower_bound AND upper_bound

  UNBOUNDED PRECEDING – All rows before the current row.
  n PRECEDING – n rows before the current row.
  CURRENT ROW – Just the current row.
  n FOLLOWING – n rows after the current row.
  UNBOUNDED FOLLOWING – All rows after the current row.
```
```

  SELECT *, AVG(amount) OVER (PARTITION BY salesperson ORDER BY sale_date ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING ) AS avg_future_sales
  FROM sales;

  SUM(amount) OVER (PARTITION BY salesperson ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
  SUM(amount) OVER ( PARTITION BY salesperson ORDER BY sale_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW ) AS running_total
  sum(weight)over(order by turn asc rows between unbounded preceding and current row )

  rank()over(order by total_weight desc)

  LEAST(from_id,to_id)

  GREATEST(from_id,to_id)

  LAG(expression [,offset[,default_value]]) OVER(ORDER BY columns)
  LAG(count,1,0) OVER(ORDER BY month) AS previous_count,
```

String format:
===========================
```
ascii('t')
char_length('Hello!')
CONCAT_WS('_', 'geeks', 'for', 'geeks')
FIND_IN_SET('b', 'a, b, c, d, e, f')
Format("0.981", "Percent")
INSTR('geeks for geeks', 'e')
INSTR('geeks for geeks', 'e', 1, 2 )
SUBSTR('geeksforgeeks', 1, 5)
POSITION('e' IN 'geeksforgeeks')
LOCATE('for', 'geeksforgeeks', 1)
LPAD('geeks', 8, '0')
LTRIM('123123geeks', '123')
TRIM(LEADING '0' FROM '000123')
LOWER('GEEKSFORGEEKS.ORG')
REPLACE('123geeks123', '123')
SPACE(7)

SUBSTRING_INDEX(): This function is used to find a sub string before the given symbol.
SUBSTRING_INDEX('www.geeksforgeeks.org', '.', 1)



```


Date format: https://www.geeksforgeeks.org/sql-date-functions/
===========================
``` 
  DATE_FORMAT(created_at, '%Y-%m') = '2020-02'
  TO_DATE( '10 Aug 2018', 'DD MON YYYY' )
  CAST('2018' AS DATE)
  date_sub(dt, interval 1 day)
  DATE_ADD(BirthTime, INTERVAL 1 YEAR)
  DATEDIFF(interval,date1, date2);           #interval – minute/hour/month/year,etc
                                            #date1 & date2- date/time expression

  Extract(DAY FROM BirthTime)
  Extract(YEAR FROM BirthTime)
  Extract(SECOND FROM 
BirthTime)
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

pivot & unpivot
=========================
```
SELECT (ColumnNames) 
FROM (TableName) 
PIVOT
 ( 
   AggregateFunction(ColumnToBeAggregated)
   FOR PivotColumn IN (PivotColumnValues)
 ) AS (Alias) //Alias is a temporary name for a table


SELECT *
FROM (
    SELECT salesperson, month, amount
    FROM sales
) AS source_table
PIVOT (
    SUM(amount)
    FOR month IN ([Jan], [Feb], [Mar])
) AS pivot_table;


| salesperson | Jan | Feb | Mar |
| ----------- | --- | --- | --- |
| Alice       | 100 | 150 | 200 |
| Bob         | 120 | 180 | 160 |


```
