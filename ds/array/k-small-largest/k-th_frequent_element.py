"""
https://leetcode.com/problems/top-k-frequent-elements/description/

Given an integer array nums and an integer k, return the k most frequent elements. You may return the answer in any order.

Example 1:

Input: nums = [1,1,1,2,2,3], k = 2
Output: [1,2]
Example 2:

Input: nums = [1], k = 1
Output: [1]

"""

class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        import heapq
        freq = {}
        out=[]
        for elem in nums:
            if elem in freq.keys():
                freq[elem]+=1
            else:
                freq[elem]=1
        # -ve because heap return smallest and by -ve it will return maximum -ve = max val
        lst = [(-freq[key], key) for key in freq.keys()]
        heapq.heapify(lst)
        print(lst)
        for i in range(k):
            out.append(heapq.heappop(lst)[1])
        return out
        
