"""
https://leetcode.com/problems/max-consecutive-ones-iii/
"""

class Solution:
    def longestOnes(self, nums: List[int], k: int) -> int:
        start, end =0, 0
        window = 0
        maxlen =0 
        dp = {}
        while end < len(nums):
            if nums[end] == 0:
                k-=1
            while k<0:
                if nums[start] == 0:
                    k+=1
                start+=1
            maxlen = max(maxlen, end-start+1)
            end+=1
        return maxlen 
        
