# 1. Python `range()` Function Cheat Sheet

The `range()` function in Python is commonly used to generate a sequence of numbers. It's frequently used in **for loops** and other situations where you need to iterate a certain number of times.

## 1.1 **Basic Syntax**
| Parameter | Description                                      | Default Value |
|-----------|--------------------------------------------------|---------------|
| `start`   | The starting number of the sequence (inclusive)  | `0`           |
| `stop`    | The ending number of the sequence (exclusive)    | Required      |
| `step`    | The step size between numbers in the sequence    | `1`           |


```python
range([start], stop[, step])

for i in range(2, 7):   
    print(i) -> 2,3,4,5,6

for i in range(4, 0, -1):  
    print(i) -> 4,3,2,1

for i in range(0, 8, 2):
    print(i) ->  0,2,4,6

my_list = list(range(5))
print(my_list) -> 0,1,2,3,4

my_range = range(5, 0, -1)
print(list(my_range))  -> 5,4,3,2,1

```

## 1.2 Using range() with enumerate():
```
my_list = ['a', 'b', 'c', 'd']
for index, value in enumerate(my_list):
    print(f"Index {index}: {value}")

Index 0: a
Index 1: b
Index 2: c
Index 3: d
```
# 2 Python List Cheat Sheet

A **list** in Python is an ordered collection of items that can be of any data type. Lists are mutable, which means you can modify them after they are created.

## 2.1. **Creating Lists**

```python
# Empty list
my_list = []

# List with integers
numbers = [1, 2, 3, 4, 5]

# List with mixed data types
mixed = [1, "apple", 3.14, True]

# List of lists (nested list)
nested_list = [[1, 2], [3, 4], [5, 6]]
```
## 2.2 Access by index
```
numbers = [10, 20, 30, 40, 50]
print(numbers[0])  # Output: 10
print(numbers[2])  # Output: 30

print(numbers[-1])  # Output: 50
```
## 2.3 Slicing Lists
```
# Slice a list from index 1 to 3 (exclusive)
print(numbers[1:4])  # Output: [20, 30, 40]

# Slice with a step
print(numbers[::2])  # Output: [10, 30, 50]

# Reverse a list
print(numbers[::-1])  # Output: [50, 40, 30, 20, 10]
```
## 2.4 Modifying Lists
```
# Change an element by index
numbers[1] = 99
print(numbers)  # Output: [10, 99, 30, 40, 50]

# Append an element to the end of the list
numbers.append(60)
print(numbers)  # Output: [10, 99, 30, 40, 50, 60]

# Insert an element at a specific position
numbers.insert(2, 25)
print(numbers)  # Output: [10, 99, 25, 30, 40, 50, 60]

# Remove an element by value
numbers.remove(99)
print(numbers)  # Output: [10, 25, 30, 40, 50, 60]

# Remove an element by index and get it
removed_element = numbers.pop(3)
print(removed_element)  # Output: 40
print(numbers)  # Output: [10, 25, 30, 50, 60]

# Clear all elements from the list
numbers.clear()
print(numbers)  # Output: []

```
## 2.5 List Operations
```
# Concatenate two lists
list1 = [1, 2, 3]
list2 = [4, 5, 6]
concatenated = list1 + list2
print(concatenated)  # Output: [1, 2, 3, 4, 5, 6]

# Repeat a list multiple times
repeated = [1, 2] * 3
print(repeated)  # Output: [1, 2, 1, 2, 1, 2]

# Check if an item exists in a list
print(3 in list1)  # Output: True
print(10 in list1)  # Output: False

```

## 2.6 List Methods
```
# Count occurrences of an element
numbers = [1, 2, 2, 3, 3, 3]
print(numbers.count(3))  # Output: 3

# Find the index of the first occurrence of an element
print(numbers.index(3))  # Output: 3

# Sort the list in ascending order
numbers = [3, 1, 4, 1, 5, 9]
numbers.sort()
print(numbers)  # Output: [1, 1, 3, 4, 5, 9]

# Sort in descending order
numbers.sort(reverse=True)
print(numbers)  # Output: [9, 5, 4, 3, 1, 1]

# Reverse the list
numbers.reverse()
print(numbers)  # Output: [1, 1, 3, 4, 5, 9]


```

## 2.7 List Conprehension
```
# Create a list of squares
squares = [x**2 for x in range(5)]
print(squares)  # Output: [0, 1, 4, 9, 16]

# Create a list of even numbers
even_numbers = [x for x in range(10) if x % 2 == 0]
print(even_numbers)  # Output: [0, 2, 4, 6, 8]


```

## 2.8 Nested Lists:
```
# Accessing nested lists
nested = [[1, 2], [3, 4], [5, 6]]
print(nested[1])    # Output: [3, 4]
print(nested[1][0]) # Output: 3

# Flatten a nested list
flattened = [item for sublist in nested for item in sublist]
print(flattened)  # Output: [1, 2, 3, 4, 5, 6]


```
# 3. Python Dictionary Cheat Sheet

A **dictionary** in Python is an unordered collection of key-value pairs. It is mutable and supports fast lookups by key.

## 3.1. **Creating a Dictionary**

```python
# Empty dictionary
my_dict = {}

# Dictionary with integer keys
age = {1: "John", 2: "Alice", 3: "Bob"}

# Dictionary with mixed data types
person = {"name": "John", "age": 30, "is_employee": True}

# Nested dictionary
employees = {
    "emp1": {"name": "Alice", "age": 25},
    "emp2": {"name": "Bob", "age": 28}
}
```
## 3.2. Accessing Values
```
# Access value by key
person = {"name": "John", "age": 30}
print(person["name"])  # Output: John

# Using .get() to avoid KeyError
print(person.get("age"))  # Output: 30
print(person.get("salary", "Not available"))  # Output: Not available

```
## 3.3. Adding or Modifying Key-Value Pairs

```
# Add a new key-value pair
person["salary"] = 50000
print(person)  # Output: {'name': 'John', 'age': 30, 'salary': 50000}

# Modify an existing value
person["age"] = 31
print(person)  # Output: {'name': 'John', 'age': 31, 'salary': 50000}


```
## ** 3.4. Removing Key-Value Pairs
```
# Using .pop() to remove a key and return its value
removed_value = person.pop("salary")
print(removed_value)  # Output: 50000
print(person)  # Output: {'name': 'John', 'age': 31}

# Using del to remove a key-value pair
del person["age"]
print(person)  # Output: {'name': 'John'}

# Using .clear() to remove all key-value pairs
person.clear()
print(person)  # Output: {}

```

## ** 3.5. Dictionary Methods
```
# Get all keys
keys = person.keys()
print(keys)  # Output: dict_keys(['name'])

# Get all values
values = person.values()
print(values)  # Output: dict_values(['John'])

# Get all key-value pairs
items = person.items()
print(items)  # Output: dict_items([('name', 'John')])

# Check if a key exists in a dictionary
print("name" in person)  # Output: True
print("age" in person)  # Output: False

# Copy the dictionary
person_copy = person.copy()
print(person_copy)  # Output: {'name': 'John'}

# Update dictionary with another dictionary or key-value pairs
person.update({"age": 30, "is_employee": True})
print(person)  # Output: {'name': 'John', 'age': 30, 'is_employee': True}

```

## 3.6. Iterating Over a Dictionary
```
# Iterate over keys
for key in person:
    print(key)

# Iterate over values
for value in person.values():
    print(value)

# Iterate over key-value pairs
for key, value in person.items():
    print(f"{key}: {value}")

```

## 3.7. Nested Dictionaries
```
# Access nested dictionary values
employees = {
    "emp1": {"name": "Alice", "age": 25},
    "emp2": {"name": "Bob", "age": 28}
}

# Access 'emp1' details
print(employees["emp1"]["name"])  # Output: Alice

```

## 3.8. Dictionary Comprehension
```
# Create a dictionary from a list of tuples
pairs = [("a", 1), ("b", 2), ("c", 3)]
my_dict = dict(pairs)
print(my_dict)  # Output: {'a': 1, 'b': 2, 'c': 3}

# Create a dictionary with square of numbers
squares = {x: x**2 for x in range(5)}
print(squares)  # Output: {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}


```
