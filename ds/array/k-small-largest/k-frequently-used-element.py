"""
https://leetcode.com/problems/top-k-frequent-elements/

Given an integer array nums and an integer k, return the k most frequent elements. You may return the answer in any order.

 

Example 1:

Input: nums = [1,1,1,2,2,3], k = 2

Output: [1,2]

Example 2:

Input: nums = [1], k = 1

Output: [1]

Example 3:

Input: nums = [1,2,1,2,1,2,3,1,3,2], k = 2

Output: [1,2]

"""
import heapq
class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        has_map = {}
        for elem in nums:
            if elem in has_map.keys():
                has_map[elem]+=1
            else:
                has_map[elem]=1
        print(has_map)
        lst = [(-has_map[i],i) for i in has_map.keys()]
        elem = []
        heapq.heapify(lst)
        for i in range(k):
            neg_val, key = heapq.heappop(lst)
            elem.append(key)
        return elem


        
