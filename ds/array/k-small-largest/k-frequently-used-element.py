"""
https://leetcode.com/problems/top-k-frequent-elements/
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


        
