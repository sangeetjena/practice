"""
https://leetcode.com/problems/longest-consecutive-sequence/description/
"""

class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        dct = {}
        for elem in nums:
            dct[elem] = 1
        visited = []
        max_len = 0
        for elem in nums:
            if elem in visited:
                continue
            temp_len = 0 
            while elem in dct.keys():
                temp_len+=1
                visited.append(elem)
                elem+=1
            max_len = max(max_len,  temp_len)
        return max_len
    
        
