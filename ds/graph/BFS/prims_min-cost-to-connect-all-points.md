```
Leetcode 1584:
https://leetcode.com/problems/min-cost-to-connect-all-points/description/

You are given an array points representing integer coordinates of some points on a 2D-plane, where points[i] = [xi, yi].

The cost of connecting two points [xi, yi] and [xj, yj] is the manhattan distance between them: |xi - xj| + |yi - yj|, where |val| denotes the absolute value of val.

Return the minimum cost to make all points connected. All points are connected if there is exactly one simple path between any two points.



Note: MST
```
<img width="632" height="814" alt="image" src="https://github.com/user-attachments/assets/9e2264c0-c710-42b7-828f-5fc562dd5329" />


``` python
import heapq
class Solution:
    def minCostConnectPoints(self, points: List[List[int]]) -> int:
        # this is simple bfs graph traversal
        visited = []
        bfs = [(0,points[0])]
        total_sum = 0
        while bfs:
            # always pull the closest point 1st, which has less distance. 
            dist, curr_point = heapq.heappop(bfs)
            if curr_point in visited:
                continue
            total_sum += dist
            # check distance from the current point to the all the points and insert it in the heap.
            for p in points:
                point = tuple(p)
                if point == curr_point or point in visited:
                    continue
                # Note: this can be improved by putting only the distance which is smallest.
                heapq.heappush(bfs, (abs(curr_point[0]-point[0]) + abs(curr_point[1]-point[1]),point))
            visited.append(curr_point)
        return total_sum
            
        
        



```
