"""
https://leetcode.com/problems/kth-smallest-element-in-a-sorted-matrix/

NOte: use heapq and pull nth smallest element.

"""
class Solution:
    def kthSmallest(self, matrix: List[List[int]], k: int) -> int:
        import heapq
        heap = []
        n=0
        small = 0
        for i in range(len(matrix)):
            heapq.heappush(heap,(matrix[i][0],i,1))
        while len(heap)>0 and n<k:
            small,arrind, ind = heapq.heappop(heap)
            n+=1
            if len(matrix[arrind])>ind:
                heapq.heappush(heap,(matrix[arrind][ind],arrind,ind+1))
        return small
