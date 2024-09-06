"""
https://leetcode.com/problems/longest-increasing-subsequence/description/
https://www.youtube.com/watch?v=mouCn3CFpgg

Given an integer array nums, return the length of the longest strictly increasing 
subsequence
.
Example 1:

Input: nums = [10,9,2,5,3,7,101,18]
Output: 4
Explanation: The longest increasing subsequence is [2,3,7,101], therefore the length is 4.
Example 2:

Input: nums = [0,1,0,3,2,3]
Output: 4

"""

class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        dp = [1 for _ in nums]
        mx = 1
        for i in range(1, len(nums)):
            for j in range(i):
                if nums[i]>nums[j]:
                    dp[i] = max(dp[i], 1+dp[j])
            mx = max(mx, dp[i])
        return mx

        
        
        
