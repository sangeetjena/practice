"""
https://leetcode.com/problems/two-sum/description/
using hash table
"""

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        dp = {}
        for i in range(0,len(nums)):
            if target - nums[i] in dp.keys():
                return [dp[target - nums[i]], i]
            dp[nums[i]] = i
        return []
