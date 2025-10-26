```
https://leetcode.com/problems/reorder-routes-to-make-all-paths-lead-to-the-city-zero/description/

There are n cities numbered from 0 to n - 1 and n - 1 roads such that there is only one way to travel between two different cities (this network form a tree).
 Last year, The ministry of transport decided to orient the roads in one direction because they are too narrow.

Roads are represented by connections where connections[i] = [ai, bi] represents a road from city ai to city bi.

This year, there will be a big event in the capital (city 0), and many people want to travel to this city.

Your task consists of reorienting some roads such that each city can visit the city 0. Return the minimum number of edges changed.

It's guaranteed that each city can reach city 0 after reorder.

Note: create hashmap and convert graph to undirected graph. then check all child node is coming inword or not and count outward childs.
```
<img width="868" height="670" alt="image" src="https://github.com/user-attachments/assets/e1cce3c3-e7d3-46c1-8477-256bf3ff9597" />

``` python
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
```


        


        
        
        
