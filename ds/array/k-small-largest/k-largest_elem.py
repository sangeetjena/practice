"""
https://leetcode.com/problems/kth-largest-element-in-an-array/

"""

import heapq
class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        lst = [-nums[i] for i in range(len(nums))]
        heapq.heapify(lst)
        elem = 0
        while k>0:
            elem = heapq.heappop(lst)
            k-=1
        print(lst)
        return -elem
