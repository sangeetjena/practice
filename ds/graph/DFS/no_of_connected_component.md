```
https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/description/

You have a graph of n nodes. You are given an integer n and an array edges where edges[i] = [ai, bi] indicates that there is an edge between ai and bi in the graph.

Return the number of connected components in the graph.

```
<img width="442" height="656" alt="image" src="https://github.com/user-attachments/assets/fa95efd2-91e6-4d68-827a-dcb4af144973" />

``` python

from collections import defaultdict
class Solution:
    def countComponents(self, n: int, edges: List[List[int]]) -> int:
        dfs = []
        dct = defaultdict(list)
        visited = []
        # as it in undirected graph so need to take parent to chield and chield to parent relation.
        for p, c in edges:
            dct[p].append(c)
            dct[c].append(p)
        count = 0
        # then simple dfs template.
        for node in range(n):
            if node in visited:
                continue
            dfs.append(node)
            count+=1
            while len(dfs)>0:
                nd = dfs[-1]
                if nd in visited:
                    del dfs[-1]
                    continue
                if dct.get(nd, None) != None:
                    for chld in dct[nd]:
                        if chld not in visited:
                            dfs.append(chld)
                visited.append(nd)
        return count
```                
                
        
