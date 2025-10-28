```
https://leetcode.com/problems/critical-connections-in-a-network/description/

here are n servers numbered from 0 to n - 1 connected by undirected server-to-server connections forming a network where connections[i] = [ai, bi] represents a connection between servers ai and bi. Any server can reach other servers directly or indirectly through the network.

A critical connection is a connection that, if removed, will make some servers unable to reach some other server.

Return all critical connections in the network in any order.

https://www.youtube.com/watch?v=qrAub5z8FeA
tarjen algorithm: https://www.youtube.com/watch?v=Rhxs4k6DyMM

Note: as per tarjen algorithm, for all node capture (node, time), during dfs if child node is less than parrent, then that will be in cycle (other path exisits to reach to the child), then update the time of parent in back tracking.
if in dfs back tracking, if parent has larger time than child then that is the critical path.

```

<img width="544" height="464" alt="image" src="https://github.com/user-attachments/assets/9908c2f7-1bdb-40f0-8e49-818af3ec8e09" />

<img width="631" height="871" alt="image" src="https://github.com/user-attachments/assets/ac526cf2-fcaf-48dd-9c40-cccd202653a9" />


``` python
from collections import defaultdict

class Solution:
    def criticalConnections(self, n: int, connections: List[List[int]]) -> List[List[int]]:
        graph = defaultdict(list)
        for u, v in connections:
            graph[u].append(v)
            graph[v].append(u)

        self.time = 0
        disc = [-1] * n   # discovery time
        low = [-1] * n    # lowest reachable discovery time
        res = []

        def dfs(u, parent):
            disc[u] = low[u] = self.time
            self.time += 1

            for v in graph[u]:
                if v == parent:
                    continue
                if disc[v] == -1:  # not visited
                    dfs(v, u)
                    low[u] = min(low[u], low[v])
                    if low[v] > disc[u]:
                        res.append([u, v])
                else:
                    low[u] = min(low[u], disc[v])

        for i in range(n):
            if disc[i] == -1:
                dfs(i, -1)

        return res




```
