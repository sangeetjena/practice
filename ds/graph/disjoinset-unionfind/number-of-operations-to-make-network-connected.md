```
https://leetcode.com/problems/number-of-operations-to-make-network-connected/description/

There are n computers numbered from 0 to n - 1 connected by ethernet cables connections forming a network where connections[i] = [ai, bi] represents a connection between computers ai and bi. Any computer can reach any other computer directly or indirectly through the network.

You are given an initial computer network connections. You can extract certain cables between two directly connected computers, and place them between any pair of disconnected computers to make them directly connected.

Return the minimum number of times you need to do this in order to make all the computers connected. If it is not possible, return -1.

Note:
solution1: find all disconnected graph then no of connection needed is = no of cluster -1. but this operation will take longer because if the node is there part of same set still we are doing parsing till we parse all the node of the cluster. ( we skipp when found in visited but still one extra operation we are using)

sol2: discjoin set or union find. we will find no of cluster (parent[node] = node) and no of duplicate edges. this has time complexity of O(1).
https://www.youtube.com/watch?v=eTaWFhPXPz4
```
<img width="816" height="624" alt="image" src="https://github.com/user-attachments/assets/3c2cde22-ddfe-4b42-8fc4-87d687a35abb" />

``` python
class DisjointSet:
    def __init__(self, n):
        self.parent = [i for i in range(n)]
        self.size = [1] * n

    def findParent(self, node):
        # check if the current node is the parent of itself (node == parent[node]), else search recurssively it parent and update it in return (path compression)
        if self.parent[node] != node:
            # how it is optiized ?
            # for 1st time it will travers all nodes, on 2nd time it will directly reach to the till now super parent by parent[node].
            # so overal time complexity is O(1).
            self.parent[node] = self.findParent(self.parent[node])
        return self.parent[node]

    def unionBySize(self, u, v):
        pu = self.findParent(u)
        pv = self.findParent(v)
        # check parent of both the nodes, if same then they are part of same cluster
        if pu == pv:
            return False  # Redundant edge
        # else check add the node to the bigger tree.
        if self.size[pu] < self.size[pv]:
            self.parent[pu] = pv
            self.size[pv] += self.size[pu]
        else:
            self.parent[pv] = pu
            self.size[pu] += self.size[pv]
        return True


class Solution:
    def makeConnected(self, n: int, connections: List[List[int]]) -> int:
        if len(connections) < n - 1:
            return -1  # Not enough edges to connect all nodes

        ds = DisjointSet(n)
        extra_edges = 0

        for u, v in connections:
            # if edge is not part of same cluster then count extra edge.
            if not ds.unionBySize(u, v):
                extra_edges += 1
        # now only the node which is parent will have same value as parent and that means those are head of cluster (no of cluster)
        components = sum(1 for i in range(n) if ds.findParent(i) == i)

        needed_edges = components - 1
        return needed_edges if extra_edges >= needed_edges else -1
```

``` python
class Solution:
    def makeConnected(self, n: int, connections: List[List[int]]) -> int:
        # if i will be able to find number of disconnected graphs are there in the network then that many connection we need to establish.
        # we also need to check if number edges there in the network is  = num nodes -1. else that network can't be established .
        # create adjacency metrics.
        dct = defaultdict(list)
        if len(connections)< n-1:
            return -1
        for node in connections:
            dct[node[0]].append(node[1])
            # as this is undirected graph so take the other way connection also.
            dct[node[1]].append(node[0])
        
        visited = []
        clusters = 0
        # simple dfs to calculate no of clusters
        for node in range(n):
            if node in visited:
                continue
            dfs = [node]
            clusters+=1
            while dfs:
                n = dfs[-1]
                del dfs[-1]
                if n in visited:
                    continue
                for c in dct[n]:
                    if c in visited:
                        continue
                    dfs.append(c)
                visited.append(n)
        # number of connction needed is = number cluster -1
        return clusters-1
        



```
