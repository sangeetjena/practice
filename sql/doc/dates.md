# Function Reference Table (Hive & MySQL)

| **Task** | **MySQL Function** | **Hive Function / Expression** | **Without Function** |
|-----------|--------------------|--------------------------------|----------------------|
| Current Date | `CURDATE()` | `CURRENT_DATE` | Not feasible |
| Current Date & Time | `NOW()` | `CURRENT_TIMESTAMP` | Not feasible |
| Convert String to Date | `STR_TO_DATE()` | `TO_DATE()`, `FROM_UNIXTIME(UNIX_TIMESTAMP())` | `SUBSTR`, `regexp` parse |
| Extract Day, Month, Year | `DAY()`, `MONTH()`, `YEAR()` | `DAY()`, `MONTH()`, `YEAR()`, `WEEKOFYEAR()`, `QUARTER()` | `SUBSTR` on `'YYYY-MM-DD'` |
| Add / Subtract Dates | `DATE_ADD()`, `DATE_SUB()` | `DATE_ADD()`, `DATE_SUB()`, `ADD_MONTHS()` | Integer math (rare) |
| Last Day of Month | `LAST_DAY()` | `LAST_DAY()` | Compose with date functions |
| Day of Week | `DAYOFWEEK()`, `DAYNAME()` | `DAYOFWEEK()`, `DATE_FORMAT('E')`, `FROM_UNIXTIME(...,'u')` | Modulo from reference date |
| Days Between Dates | `DATEDIFF()` | `DATEDIFF()` | Arithmetic with preprocessed dates |
| Week Number | `WEEK()` | `WEEKOFYEAR()` | `(DAYOFYEAR-1)/7+1` |
| Employees Joined Last 6 Months | `DATE_SUB(CURDATE(), INTERVAL 6 MONTH)` | `ADD_MONTHS(CURRENT_DATE(), -6)` | Pre-calculate reference date |
| Employees Birthday This Month | `MONTH(birth_date)` | `MONTH(birth_date) = MONTH(CURRENT_DATE())` | Compare substrings |
| Generate All Dates in Range | Recursive CTE, helper table | LATERAL VIEW with sequence / UDF / helper table | Pre-generated list |
| Age Calculation | `DATEDIFF(CURDATE(), birth_date)/365` | `DATEDIFF(CURRENT_DATE(), birth_date)/365` | Difference in year substrings |


# Comprehensive Guide to SQL Date Functions (Hive & MySQL)

## Overview
Apache Hive, widely used in big data analytics, provides a rich set of date and time functions.  
This guide covers the essentials for everyday and advanced scenarios—including converting strings to dates, extracting date components, date arithmetic, and querying for ranges—using Hive and MySQL.  
Where possible, alternatives without built-in functions are also illustrated.

---

## Core Date Functions

### Getting the Current Date & Time

**MySQL:**
```sql
SELECT CURDATE();          -- Current Date
SELECT CURTIME();          -- Current Time
SELECT NOW();              -- Date & Time
```

**Hive:**
```sql
SELECT CURRENT_DATE;       -- Current Date
SELECT CURRENT_TIMESTAMP;  -- Current Timestamp
```

**Without Built-in Functions:**  
Not feasible; requires external preprocessing.

---

### Convert String to Date

**MySQL:**
```sql
SELECT STR_TO_DATE('10-12-2023', '%d-%m-%Y');
```

**Hive:**
```sql
SELECT TO_DATE('2020-04-01 13:04:05.000');
-- With explicit format
SELECT TO_DATE('2020-04-01 13:04:05.000');
-- For custom formats
SELECT FROM_UNIXTIME(UNIX_TIMESTAMP('10-12-2023', 'dd-MM-yyyy'));
```

**Without Built-in Functions:**  
Manual string parsing using substring/regexp, but error-prone and not scalable.

---

### Extract Day, Month, Year

**MySQL:**
```sql
SELECT DAY('2020-12-02');
SELECT MONTH('2020-12-02');
SELECT YEAR('2020-12-02');
```

**Hive:**
```sql
SELECT YEAR('2020-11-11');
SELECT MONTH('2020-11-11');
SELECT DAY('2020-11-11');
SELECT DAYOFMONTH('2020-11-11');
SELECT WEEKOFYEAR('2020-11-11');  -- Week of year
SELECT QUARTER('2020-11-11');     -- Quarter
```

**Without Built-in Functions:**
```sql
-- Assuming date string format 'YYYY-MM-DD'
SELECT SUBSTR(date_str, 1, 4) AS year,
       SUBSTR(date_str, 6, 2) AS month,
       SUBSTR(date_str, 9, 2) AS day;
```

---

### Date Addition & Subtraction

**MySQL:**
```sql
SELECT DATE_ADD('2023-10-10', INTERVAL 5 DAY);
SELECT DATE_SUB('2023-10-10', INTERVAL 5 DAY);
```

**Hive:**
```sql
SELECT DATE_ADD('2025-05-20', 10);
SELECT DATE_SUB('2025-05-20', 10);
SELECT ADD_MONTHS('2025-05-20', 2);
```

**Without Built-in Functions:**  
Requires date as integer or external logic; not recommended.

---

### Last Day of the Month

**MySQL:**
```sql
SELECT LAST_DAY('2023-10-15');
```

**Hive:**
```sql
SELECT LAST_DAY('2023-10-15');
```

**Without Built-in Functions:**
```sql
SELECT TO_DATE(
    DATE_SUB(
        ADD_MONTHS(CONCAT(FROM_UNIXTIME(UNIX_TIMESTAMP('2023-10-15','yyyy-MM-dd'), 'yyyy-MM'),'-01'),1),
        1
    )
);
```

---

### Day of the Week

**MySQL:**
```sql
SELECT DAYOFWEEK('2023-10-15');
```

**Hive:**
```sql
SELECT DAYOFWEEK('2023-10-15');
SELECT DATE_FORMAT('2023-10-15','E');  -- Day name
SELECT FROM_UNIXTIME(UNIX_TIMESTAMP('2023-10-15','yyyy-MM-dd'),'u');
```

**Without Built-in Functions:**  
Calculate by difference from reference date, modulo 7; not practical in SQL.

---

### Days Between Two Dates

**MySQL:**
```sql
SELECT DATEDIFF('2021-12-25', '2021-01-01');
```

**Hive:**
```sql
SELECT DATEDIFF('2021-12-25', '2021-01-01');
```

**Without Built-in Functions:**  
Convert both dates to integer (Julian date), then subtract; not recommended.

---

### Employees Joined in Last 6 Months

Assuming table column: `join_date`

**MySQL:**
```sql
SELECT * 
FROM employees 
WHERE join_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH);
```

**Hive:**
```sql
SELECT * 
FROM employees 
WHERE join_date >= ADD_MONTHS(CURRENT_DATE(), -6);
```

**Without Built-in Functions:**  
Pre-calculate “6 months ago” date externally and filter on string.

---

### Employees with Birthdays This Month

**MySQL:**
```sql
SELECT * 
FROM employees 
WHERE MONTH(birth_date) = MONTH(CURDATE());
```

**Hive:**
```sql
SELECT * 
FROM employees 
WHERE MONTH(birth_date) = MONTH(CURRENT_DATE());
```

**Without Built-in Functions:**
```sql
SUBSTR(birth_date,6,2) = SUBSTR(CURRENT_DATE,6,2)
```

---

### Generate All Dates Between Two Dates

**MySQL/Hive:**
Use recursive CTE (MySQL) or generate date sequence with UDF or evaluation loop in Hive.

**Hive pattern:**
```sql
-- Using LATERAL VIEW or custom UDF
-- to generate date series between start_date and end_date
```

**Without Built-in Functions:**  
Generate externally, insert as helper table.

---

### Age Calculation from Birthdate

**MySQL:**
```sql
SELECT FLOOR(DATEDIFF(CURDATE(), birth_date) / 365.25) FROM employees;
```

**Hive:**
```sql
SELECT FLOOR(DATEDIFF(CURRENT_DATE(), birth_date) / 365.25) FROM employees;
```

**Without Built-in Functions:**
```sql
SELECT CAST(SUBSTR(CURRENT_DATE(),1,4) AS INT) - 
       CAST(SUBSTR(birth_date,1,4) AS INT);
```

---

### Week Number for a Date

**MySQL:**
```sql
SELECT WEEK('2023-10-15');
```

**Hive:**
```sql
SELECT WEEKOFYEAR('2023-10-15');
```

**Without Built-in Functions:**
```sql
-- Assuming DAYOFYEAR function is available
SELECT INT((DAYOFYEAR(date) - 1) / 7) + 1;
```

---
