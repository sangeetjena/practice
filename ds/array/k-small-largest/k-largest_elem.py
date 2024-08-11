"""
https://leetcode.com/problems/kth-largest-element-in-an-array/

Given an integer array nums and an integer k, return the kth largest element in the array.

Note that it is the kth largest element in the sorted order, not the kth distinct element.

Can you solve it without sorting?

 

Example 1:

Input: nums = [3,2,1,5,6,4], k = 2
Output: 5

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
