# Extensive Guide to SQL String Functions (MySQL & Hive)

## Overview
String operations form the backbone of data cleansing, formatting, pattern matching, and textual analysis in SQL.  
Both **MySQL** and **Hive** offer extensive inbuilt functions for string manipulation, along with strategies for manual processing where required.

---

## Core String Functions

### Concatenation

**MySQL**
```sql
SELECT CONCAT('John', ' ', 'Doe');  -- Combines multiple strings
SELECT CONCAT_WS(',', 'Apple', NULL, 'Banana');  -- Skips NULL values
```

**Hive**
```sql
SELECT CONCAT('John', ' ', 'Doe');
SELECT CONCAT_WS(',', 'Apple', NULL, 'Banana');
```

---

### Length

**MySQL**
```sql
SELECT CHAR_LENGTH('Hello'), LENGTH('Hello');
```

**Hive**
```sql
SELECT LENGTH('Hello'), CHARACTER_LENGTH('Hello');
```

---

### Case Manipulation

**MySQL**
```sql
SELECT UPPER('hello'), LOWER('HELLO');
```

**Hive**
```sql
SELECT UPPER('hello'), LOWER('HELLO');
```

---

### Substring Extraction

**MySQL**
```sql
SELECT SUBSTRING('HelloWorld', 1, 5);  -- 'Hello'
```

**Hive**
```sql
SELECT SUBSTR('HelloWorld', 1, 5);     -- 'Hello'
SELECT SUBSTRING('HelloWorld', 1, 5);
```

---

### Trimming and Padding

**MySQL**
```sql
SELECT TRIM(' Hello ');
SELECT LTRIM(' Hello ');
SELECT RTRIM(' Hello ');
SELECT LPAD('abc', 5, 'x');  -- 'xxabc'
SELECT RPAD('abc', 5, 'x');  -- 'abcxx'
```

**Hive**
```sql
SELECT TRIM(' Hello ');
SELECT LTRIM(' Hello ');
SELECT RTRIM(' Hello ');
SELECT LPAD('abc', 5, 'x');
SELECT RPAD('abc', 5, 'x');
```

---

### Search & Replace

**MySQL**
```sql
SELECT INSTR('abcdef', 'cd');                  -- Returns index
SELECT REPLACE('abcabc', 'a', 'x');            -- Replace all 'a'
```

**Hive**
```sql
SELECT INSTR('abcdef', 'cd');
SELECT REPLACE('abcabc', 'a', 'x');
```

---

### Splitting and Joining

**MySQL**
```sql
-- No native SPLIT, use SUBSTRING_INDEX
SELECT SUBSTRING_INDEX('a-b-c', '-', 1);
```

**Hive**
```sql
SELECT SPLIT('a-b-c', '-');         -- Returns ['a','b','c']
SELECT CONCAT_WS('-', 'a', 'b', 'c');  -- Joins with delimiter
```

---

## Other Essential Operations

| **Operation** | **MySQL** | **Hive** |
|----------------|------------|-----------|
| Reverse String | `REVERSE()` | `REVERSE()` |
| Format Number | No direct | `FORMAT_NUMBER()` |
| ASCII Value | `ASCII()` | `ASCII()` |
| Unicode Value | `UNICODE()` | No direct |
| Find Substring | `LOCATE()` | `INSTR()` |
| Soundex/Phonetic | `SOUNDEX()` | `SOUNDEX()` |
| Translate Chars | `TRANSLATE()` | `TRANSLATE()` |
| Get N-th word | `ELT()` | `ELT()` |
| Replace Multiple | Nested `REPLACE()` | Nested `REPLACE()` |

---

## Interview-Style String Manipulation Questions

### 1. Extract Domain from an Email
**MySQL**
```sql
SELECT SUBSTRING_INDEX(email, '@', -1);
```

**Hive**
```sql
SELECT SPLIT(email, '@')[1];
```

---

### 2. Find Palindromes
```sql
SELECT word FROM words WHERE word = REVERSE(word);
```

---

### 3. Count Occurrences of a Substring
```sql
SELECT (LENGTH(text) - LENGTH(REPLACE(text, 'sub', ''))) / LENGTH('sub');
```

---

### 4. Remove All Whitespaces
```sql
SELECT REPLACE(text, ' ', '');
```

---

### 5. Check if String Contains Only Digits
```sql
SELECT * FROM t WHERE col REGEXP '^[0-9]+$';
-- Hive: WHERE col RLIKE '^[0-9]+$'
```

---

### 6. Extract Numeric Portion from String
**Hive**
```sql
SELECT REGEXP_EXTRACT(text, '[0-9]+');
```

**MySQL**
```sql
SELECT SUBSTRING(text, LOCATE('0', text), LENGTH(text));
```

---

### 7. Split Full Name into First and Last
**Hive**
```sql
SELECT SPLIT(name, ' ')[0] AS first_name, SPLIT(name, ' ')[1] AS last_name;
```

**MySQL**
```sql
SELECT SUBSTRING_INDEX(name, ' ', 1) AS first_name,
       SUBSTRING_INDEX(name, ' ', -1) AS last_name;
```

---

### 8. Efficient Fuzzy Search / LIKE
```sql
SELECT * FROM users WHERE name LIKE '%foo%';
-- Hive alternative: WHERE name RLIKE 'foo'
```

---

## Additional Hive Functions for Advanced String Operations

- `LENGTH()`, `CHARACTER_LENGTH()`
- `REGEXP_REPLACE(str, pattern, replacement)`
- `REGEXP_EXTRACT(str, pattern, group)`
- `SPACE(n)` → Generates a string with *n* spaces
- `PARSE_URL()` → Extracts parts of a URL
- `FIND_IN_SET()` → Finds element position in a delimited string
- `BASE64()`, `UNBASE64()` → Encoding/decoding
- `SPLIT(str, delimiter)` → Returns array

---

## Function Table (MySQL vs Hive)

| **Function** | **MySQL Syntax** | **Hive Syntax** | **Manual / Alternatives** |
|---------------|------------------|------------------|----------------------------|
| Length | `LENGTH(str)` | `LENGTH(str)` | Count via loop |
| Uppercase | `UPPER(str)` | `UPPER(str)` | N/A |
| Lowercase | `LOWER(str)` | `LOWER(str)` | N/A |
| Substring | `SUBSTRING(str, pos, len)` | `SUBSTR(str, pos, len)` | N/A |
| Trim | `TRIM(str)` | `TRIM(str)` | Manual check |
| Padding | `LPAD(str,n,ch)` / `RPAD(str,n,ch)` | `LPAD(str,n,ch)` / `RPAD(str,n,ch)` | String concat |
| Replace | `REPLACE(str, old, new)` | `REPLACE(str, old, new)` | Loop logic |
| Reverse | `REVERSE(str)` | `REVERSE(str)` | Loop index |
| Split | `SUBSTRING_INDEX()` | `SPLIT(str, delim)` | Manual parsing |
| Join | `CONCAT_WS(sep,...)` | `CONCAT_WS(sep,...)` | Concat loop |
| Search Position | `INSTR(str, substr)` | `INSTR(str, substr)` | Manual index |
| Regex Search | `REGEXP` | `RLIKE`, `REGEXP_REPLACE`, `REGEXP_EXTRACT` | N/A |
| Format Number | N/A | `FORMAT_NUMBER(num, dec)` | N/A |
| ASCII/Unicode | `ASCII(str)`, `UNICODE(str)` | `ASCII(str)` | Code lookup |

> *Note: MySQL has limited array support, making splitting less flexible. Hive provides native array and map operations.*

---

## Common Interview Concepts and Patterns

- Pattern matching using `LIKE`, `REGEXP`, `RLIKE`
- Case normalization before joins/grouping
- Data cleaning using `TRIM`, `REPLACE`, `REGEXP_REPLACE`
- Complex extractions using combinations of `SUBSTR`, `SPLIT`, `REGEXP_EXTRACT`
- Case-insensitive comparisons with `UPPER()` / `LOWER()`
- Fuzzy search using `SOUNDEX()`
- Finding duplicates, anagrams, or palindromes
- Splitting CSV fields or lists into arrays (Hive)
- Combining arrays using `EXPLODE()` and `CONCAT_WS()`

---

## Advanced Usage in Hive

- Work with **array and map functions** (`split`, `explode`)
- Chain multiple string functions for text normalization
- Perform efficient substring search in large datasets
- Handle **UTF-8 and ASCII encoding** carefully
- Create **UDFs** for complex or reusable string transformations

---

### Summary
This document serves as a **comprehensive reference** for SQL string manipulation in **MySQL** and **Hive** — covering built-in functions, manual alternatives, and patterns frequently tested in **interviews** and used in **production-grade data pipelines**.
