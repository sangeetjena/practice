"""
https://leetcode.com/problems/reorder-routes-to-make-all-paths-lead-to-the-city-zero/description/

Note: create hashmap and convert graph to undirected graph. then check all child node is coming inword or not and count outward childs.
"""
from collections import deque
class Solution:
    def minReorder(self, n: int, connections: List[List[int]]) -> int:
        conn  = defaultdict(list)
        dct = defaultdict(list)
        # convert graph to undirected graph to be able to travers all node
        # create mapping of exisiting connections
        for a,b in connections:
            conn[a].append(b)
            conn[b].append(a)
            dct[a].append(b)
        queue = deque([(0,-1)])
        count=0
        print(dct)
        while len(queue)>0:
            node, parent = queue.popleft()
            for n in conn[node]:
                # skip is node taken is parent node of current node
                if n == parent:
                    continue
                queue.append((n,node))
                # check if direction from parent to child is outword then change is needed and increment cont.
                if n in dct.get(node, []):
                    count+=1
                print(node,parent,n,count)
        return count



        


        
        
        
