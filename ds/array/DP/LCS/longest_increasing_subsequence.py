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


Note:
it is similar to the bobble sort. 
j-i
j--i
j----i
where j and i will start from same posistion then i will keep increasing and j will catchup from 0 to i
if value at i is greater than val(j) that means new LIS found and it length will be legth at [(j) +1]
"""

class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        dp = [1 for _ in range(len(nums))]
        mx = 1
        for i in range(len(nums)):
            for j in range(i):
                # that means increasing subsequence possible
                if nums[i] > nums[j]:
                    dp[i] = max(dp[i], 1+dp[j])
        return max(dp)

        
        
        
