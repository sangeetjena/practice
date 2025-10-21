```
https://leetcode.com/problems/graph-valid-tree/description/

You have a graph of n nodes labeled from 0 to n - 1. You are given an integer n and a list of edges where edges[i] = [ai, bi] indicates that there is an undirected edge between nodes ai and bi in the graph.

Return true if the edges of the given graph make up a valid tree, and false otherwise.

note: for a valida tree, there should not be any cycle and all the node should have visited at the end of dfs traversal,

```
<img width="543" height="749" alt="image" src="https://github.com/user-attachments/assets/098e2286-f6d6-4f26-8d69-43bb4c926b80" />


``` python
from collections import defaultdict
class Solution:
    def validTree(self, n: int, edges: List[List[int]]) -> bool:
        # we need to find if there is no cycle in the graph.
        visited = []
        bfs = [0]
        graph = defaultdict(set)
        for parent, chield in edges:
            # for undirected graph store both ((p->c) and (c->p))
            graph[parent].add(chield)
            graph[chield].add(parent)
        while bfs:
            node = bfs[-1]
            if node in visited:
                return False
            del bfs[-1]
            for chield in graph[node]:
                bfs.append(chield)
                # if child already added to the dfs, remove reverse store (child storing parent information) for undirected graph (p->c) and (c->p) to avoid reprocessing same edge.
                graph[chield].remove(node)
            if node not in visited:
                visited.append(node)
        return True if len(visited) == n else False
```
