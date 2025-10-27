```
https://leetcode.com/problems/number-of-operations-to-make-network-connected/description/

There are n computers numbered from 0 to n - 1 connected by ethernet cables connections forming a network where connections[i] = [ai, bi] represents a connection between computers ai and bi. Any computer can reach any other computer directly or indirectly through the network.

You are given an initial computer network connections. You can extract certain cables between two directly connected computers, and place them between any pair of disconnected computers to make them directly connected.

Return the minimum number of times you need to do this in order to make all the computers connected. If it is not possible, return -1.

Note:
solution1: find all disconnected graph then no of connection needed is = no of cluster -1
```
<img width="816" height="624" alt="image" src="https://github.com/user-attachments/assets/3c2cde22-ddfe-4b42-8fc4-87d687a35abb" />



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
