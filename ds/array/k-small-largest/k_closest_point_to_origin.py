"""

https://leetcode.com/problems/k-closest-points-to-origin/description/

Given an array of points where points[i] = [xi, yi] represents a point on the X-Y plane and an integer k, return the k closest points to the origin (0, 0).

The distance between two points on the X-Y plane is the Euclidean distance (i.e., √(x1 - x2)2 + (y1 - y2)2).

You may return the answer in any order. The answer is guaranteed to be unique (except for the order that it is in).

Input: points = [[1,3],[-2,2]], k = 1
Output: [[-2,2]]
Explanation:
The distance between (1, 3) and the origin is sqrt(10).
The distance between (-2, 2) and the origin is sqrt(8).
Since sqrt(8) < sqrt(10), (-2, 2) is closer to the origin.
We only want the closest k = 1 points from the origin, so the answer is just [[-2,2]].
"""

class Solution:
    def kClosest(self, points: List[List[int]], k: int) -> List[List[int]]:
        import heapq
        heap = [(-1 * (points[i][0] ** 2 + points[i][1] ** 2), i) for i in range(k)]
        heapq.heapify(heap)
        for i in range(k, len(points)):
            curr = (-1 * (points[i][0] ** 2 + points[i][1] ** 2))
            if curr > heap[0][0]:
                heapq.heappushpop(heap,(curr,i))
        return [points[i] for _,i in heap]
        
