"""
https://leetcode.com/problems/graph-valid-tree/description/



Note: 
1- create adjacenty map
2- check edges = n-1
3- add dfs ( node and parent)
4- check if child nodes in visited list then cycle detected and retrun false, if child node is parent avoid it and continue.
5- if no of disconnected graph is >1 return false


"""
==========DFS =============
class Solution:
    def validTree(self, n: int, edges: List[List[int]]) -> bool:
        # for a valid tree no of adges will be no of node -1
        if len(edges)!=n-1:
            return False
        dct = defaultdict(list)
        # for undirected graph edgecenty list will containe parent to child and child to parent relation.
        for p,c in edges:
            dct[p].append(c)
            dct[c].append(p)
        # for undirected graph extra cycle variable is not needed as we can move unrestrictedly upward or downward.
        visited = []
        dfs = []
        cnt =0
        for key in dct.keys():
            if key in visited:
                continue
            # node and parent node to avoid self loop in undirected graph.
            dfs.append((key,-1))
            cnt+=1
            while len(dfs)>0:
                node, parent = dfs[-1]
                if node in visited:
                    del dfs[-1]
                    continue
                for chld in dct[node]:
                    # if child is pointing to parent then avoid it as it is undirected graph
                    if chld == parent:
                        continue
                    if chld in visited:
                        return False
                    dfs.append((chld, node))
                visited.append(node)
        # for disconnnected graph only cnt value will become > 1
        if cnt >1:
            return False
        return True
        
==========BFS ============
from collections import deque
class Solution:
    def validTree(self, n: int, edges: List[List[int]]) -> bool:
        # for a valid tree no of adges will be no of node -1
        if len(edges)!=n-1:
            return False
        dct = defaultdict(list)
        # for undirected graph edgecenty list will containe parent to child and child to parent relation.
        for p,c in edges:
            dct[p].append(c)
            dct[c].append(p)
        # for undirected graph extra cycle variable is not needed as we can move unrestrictedly upward or downward.
        visited = []
        bfs  = deque([])
        cnt = 0
        for k in dct.keys():
            if k in visited:
                continue
            cnt+=1
            bfs.append((k,-1))
            while len(bfs)>0:
                node, parent = bfs.popleft()
                visited.append(node)
                for k in dct[node]:
                    if k == parent:
                        continue
                    if k in visited:
                        return False
                    bfs.append((k, node))
            if cnt>1:
                return False
        return True
        

            
        
