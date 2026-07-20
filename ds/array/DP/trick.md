# Dynamic Programming Pattern Recognition Cheat Sheet

A quick reference to identify common DP patterns during interviews and LeetCode practice.

---

# 1. Fibonacci Pattern (Linear DP)

## Quick Hints
- Linear sequence (array, stairs, houses, days)
- `dp[i]` depends on only a few previous states
- Usually previous 1, 2, or k states

## Ask Yourself
> **Can I reach the current state from only a few previous states?**

## State
```cpp
dp[i]
```

## Typical Transition
```cpp
dp[i] = f(dp[i-1], dp[i-2])
```

## Recognition
- One-dimensional DP
- Local transitions only
- No need to remember the entire history

## Classic Problems
- Fibonacci Number
- Climbing Stairs
- Min Cost Climbing Stairs
- House Robber I
- House Robber II
- Decode Ways

---

# 2. Longest Common Subsequence (LCS Pattern)

## Quick Hints
- Two strings
- Two arrays
- Compare prefixes
- Match / Don't Match

## Ask Yourself
> **Am I comparing two sequences?**

## State
```cpp
dp[i][j]
```

## Typical Transition
```cpp
if (a[i] == b[j])
    dp[i][j] = dp[i-1][j-1] + 1;
else
    dp[i][j] = max(dp[i-1][j], dp[i][j-1]);
```

## Recognition
- Two indices
- Prefix vs Prefix
- Alignment/comparison problems

## Classic Problems
- Longest Common Subsequence
- Edit Distance
- Delete Operation for Two Strings
- Distinct Subsequences
- Wildcard Matching

---

# 3. Longest Increasing Subsequence (LIS Pattern)

## Quick Hints
- Increasing
- Decreasing
- Chain
- Previous smaller/larger element

## Ask Yourself
> **Can I extend a valid sequence using previous elements?**

## State
```cpp
dp[i]
```

## Typical Transition
```cpp
dp[i] = max(dp[j] + 1)
```

for every

```cpp
j < i
```

## Recognition
- Compare current element with previous elements
- Previous state is NOT fixed (can be any previous element)

## Classic Problems
- Longest Increasing Subsequence
- Russian Doll Envelopes
- Number of LIS
- Largest Divisible Subset
- Maximum Length of Pair Chain

---

# 4. 0/1 Knapsack Pattern

## Quick Hints
- Pick or Skip
- Capacity
- Weight
- Budget
- Resource constraints

## Ask Yourself
> **For every item, do I have two choices: take it or leave it?**

## State
```cpp
dp[item][capacity]
```

## Typical Transition
```cpp
Take
Skip
```

## Recognition
- Binary decision
- Capacity changes after taking an item

## Classic Problems
- 0/1 Knapsack
- Partition Equal Subset Sum
- Target Sum
- Last Stone Weight II
- Ones and Zeroes

---

# 5. Bitmask DP (State Compression DP)

## Quick Hints
- N ≤ 20
- Visited
- Used
- Chosen
- Assignments
- Permutations

## Ask Yourself
> **Can my state be represented as a subset of elements?**

## State
```cpp
dp[mask]
```

or

```cpp
dp[mask][last]
```

## Typical Transition
```cpp
Choose next unused element
```

## Recognition
- State = subset
- Same subset appears many times
- DFS + Memoization works naturally

## Classic Problems
- Traveling Salesman Problem
- Android Unlock Patterns
- Can I Win
- Beautiful Arrangement
- Partition to K Equal Sum Subsets
- Shortest Path Visiting All Nodes

---

# 6. Interval DP

## Quick Hints
- Subarray
- Parentheses
- Palindrome
- Burst
- Merge

## Ask Yourself
> **Is my state an interval [l...r]?**

## State
```cpp
dp[l][r]
```

## Typical Transition
```cpp
Split interval at k
```

## Recognition
- Solve smaller intervals first
- Expand interval size gradually

## Classic Problems
- Burst Balloons
- Matrix Chain Multiplication
- Minimum Cost to Cut a Stick
- Palindrome Partitioning II
- Strange Printer

---

# 7. Tree DP

## Quick Hints
- Binary tree
- Graph without cycles
- Parent-child relationship

## Ask Yourself
> **Can I compute my answer from my children's answers?**

## State
```cpp
dp[node]
```

or

```cpp
dfs(node)
```

## Typical Transition
```cpp
Combine answers from children
```

## Recognition
- DFS
- Post-order traversal
- Parent depends on children

## Classic Problems
- House Robber III
- Binary Tree Cameras
- Diameter of Binary Tree
- Maximum Path Sum
- Tree Matching

---

# 8. Digit DP

## Quick Hints
- Range [0...N]
- Digits
- Count numbers
- Constraints on digits

## Ask Yourself
> **Am I constructing numbers digit by digit?**

## State
```cpp
dp(pos, tight, ...)
```

## Typical Transition
```cpp
Try every possible digit
```

## Recognition
- Upper bound N
- Tight flag
- Leading zero flag

## Classic Problems
- Count Special Integers
- Numbers With Repeated Digits
- Count Digit One
- Count Numbers With Unique Digits

---

# DP Recognition Flow

```
Linear sequence?
    ├── Yes → Fibonacci Pattern

Two strings?
    ├── Yes → LCS Pattern

Increasing/Decreasing?
    ├── Yes → LIS Pattern

Pick or Skip?
    ├── Yes → Knapsack Pattern

Subset / Visited / N ≤ 20?
    ├── Yes → Bitmask DP

Interval [l...r]?
    ├── Yes → Interval DP

Tree?
    ├── Yes → Tree DP

Digits up to N?
    ├── Yes → Digit DP
```
