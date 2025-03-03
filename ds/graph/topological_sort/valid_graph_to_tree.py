"""
https://leetcode.com/problems/graph-valid-tree/description/

note: one single child will not be pointed by, 2 parent node

"""
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
