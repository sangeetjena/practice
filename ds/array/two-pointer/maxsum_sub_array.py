"""
https://leetcode.com/problems/maximum-subarray/description/?envType=company&envId=linkedin&favoriteSlug=linkedin-thirty-days

Given an integer array nums, find the 
subarray
 with the largest sum, and return its sum.

 

Example 1:

Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
Output: 6
Explanation: The subarray [4,-1,2,1] has the largest sum 6.
Example 2:

Input: nums = [1]
Output: 1
Explanation: The subarray [1] has the largest sum 1.

Note: This is two ponter problem . expand the window untill find a negetive sum else keep expanding the window.

"""

class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        # this is two ponter problem . expand the window untill find a negetive sum else keep expanding the window.
        r = 0
        totalSum = 0
        maxSum = -float("inf")
        while r< len(nums):
            totalSum+=nums[r] 
            maxSum = max(maxSum, totalSum)
            if totalSum < 0:
                totalSum = 0
            r+=1
        return maxSum
        
