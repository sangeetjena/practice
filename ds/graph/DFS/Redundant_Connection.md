```
https://leetcode.com/problems/redundant-connection/

In this problem, a tree is an undirected graph that is connected and has no cycles.

You are given a graph that started as a tree with n nodes labeled from 1 to n, with one additional edge added.
The added edge has two different vertices chosen from 1 to n, and was not an edge that already existed.
The graph is represented as an array edges of length n where edges[i] = [ai, bi]
indicates that there is an edge between nodes ai and bi in the graph.

Return an edge that can be removed so that the resulting graph is a tree of n nodes.
If there are multiple answers, return the answer that occurs last in the input.

Note:
1 - detect cycle node using dfs
2 - union find (optimized)
```
<img width="500" height="673" alt="image" src="https://github.com/user-attachments/assets/a8a7547e-a78f-4c74-b92e-8a91fc010d3e" />

``` python
class Solution:
    def findRedundantConnection(self, edges: List[List[int]]) -> List[int]:
        unionset = [i for i in range(len(edges))]
        extraedges = []
        def find(node):
            # sind super parent and set all the child with its supream parent.
            if node != unionset[node]:
                unionset[node] = find(unionset[node])
            # return super parent value.
            return unionset[node]
        def unionfind(node1, node2):
            p1 = find(node1)
            p2 = find(node2)
            # check if two node parents are same or not.
            if p1 == p2:
                extraedges.append([node1+1,node2+1])
            else:
                # if parent are differnt then create a link and set relation with super parent.
                unionset[p1] = node2
            print(f'for {node1} {node2} parents are {p1} {p2} {unionset}')
        # just did node -1, as unionset i have created from index 0 and above added one to regenerate node value.
        for edge in edges:
            unionfind(edge[0]-1, edge[1]-1)
        # need only last element.
        return extraedges[-1]



```
