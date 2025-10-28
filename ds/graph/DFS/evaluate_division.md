```
## Uber
https://leetcode.com/problems/evaluate-division/description/

You are given an array of variable pairs equations and an array of real numbers values, where equations[i] = [Ai, Bi] 
and values[i] represent the equation Ai / Bi = values[i]. Each Ai or Bi is a string that represents a single variable.

You are also given some queries, where queries[j] = [Cj, Dj] represents the jth query where you must find the answer for Cj / Dj = ?.

Return the answers to all queries. If a single answer cannot be determined, return -1.0.

Note: The input is always valid. You may assume that evaluating the queries will not result in division by zero and 
that there is no contradiction.

Note: simple dfs solution, from one edge if we can reach to other edges where the destination value is present or not.
.if not able to find in one route, then in backtraking devide the value from the total and search for other route and multiply
the value, till you reach the final node.
The variables that do not occur in the list of equations are undefined, so the answer cannot be determined for them.

 

Example 1:

Input: equations = [["a","b"],["b","c"]], values = [2.0,3.0], queries = [["a","c"],["b","a"],["a","e"],["a","a"],["x","x"]]
Output: [6.00000,0.50000,-1.00000,1.00000,-1.00000]
Explanation: 
Given: a / b = 2.0, b / c = 3.0
queries are: a / c = ?, b / a = ?, a / e = ?, a / a = ?, x / x = ? 
return: [6.0, 0.5, -1.0, 1.0, -1.0 ]
note: x is undefined => -1.0
Example 2:

Input: equations = [["a","b"],["b","c"],["bc","cd"]], values = [1.5,2.5,5.0], queries = [["a","c"],["c","b"],["bc","cd"],["cd","bc"]]
Output: [3.75000,0.40000,5.00000,0.20000]
Example 3:

Input: equations = [["a","b"]], values = [0.5], queries = [["a","b"],["b","a"],["a","c"],["x","y"]]
Output: [0.50000,2.00000,-1.00000,-1.00000]


Note: simple dfs probelm, just add reverse entry (a-> and b->a) in adjacency dictionary

```


``` python
from collections import defaultdict
class Solution:
    def calcEquation(self, equations: List[List[str]], values: List[float], queries: List[List[str]]) -> List[float]:
        # capture reverse devide for each combination. and create adjecency metrics.
        final = []
        dct = defaultdict(list)
        for i in range(len(equations)):
            dct[equations[i][0]].append([equations[i][1],values[i]])
            dct[equations[i][1]].append([equations[i][0],1/values[i]])
        # run graph traversal for each queries.
        print(dct)
        print()
        for i in range(len(queries)):
            start, end = queries[i]
            # if searching key is not present in dict then simply retrun -1
            if start not in dct.keys():
                final.append(-1.00000)
                continue
            dfs = [[start,1]]
            tempres = 1
            visited = []
            final.append(-1.00000)
            print(f'search for {start} and {end}')
            while dfs:
                node , val = dfs[-1]
                # first check visited list and remove elemet to avoid double multiplication during back tracking.
                if node in visited:
                    tempres/=val
                    del dfs[-1]
                    continue
                tempres*=val
                print(node, val, tempres)
                if node == end:
                    final[-1] = tempres
                    break
                
                for elem in dct[node]:
                    if elem[0] not in visited:
                        dfs.append(elem)
                visited.append(node)
        return final
```

            
        




```
