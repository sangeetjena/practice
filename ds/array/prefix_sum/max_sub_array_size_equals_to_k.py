"""
https://leetcode.com/problems/maximum-size-subarray-sum-equals-k/description/

Given an integer array nums and an integer k, return the maximum length of a subarray that sums to k. If there is not one, return 0 instead.

 

Example 1:

Input: nums = [1,-1,5,-2,3], k = 3
Output: 4
Explanation: The subarray [1, -1, 5, -2] sums to 3 and is the longest.
Example 2:

Input: nums = [-2,-1,2,1], k = 1
Output: 2
Explanation: The subarray [-1, 2] sums to 1 and is the longest.
 




"""

class Solution:
    def maxSubArrayLen(self, nums: List[int], k: int) -> int:
        # same as sub array sum = k additionaly capture 1st index postiton of total
        prefix_sum = {} 
        total = 0
        maxlen = 0
        for i in range(len(nums)):
            total += nums[i]
            if total == k:
                maxlen = max(maxlen, i+1)
            if total-k  in prefix_sum.keys():
                maxlen = max(maxlen, i- prefix_sum[total-k])
            if total not in prefix_sum.keys():
                prefix_sum[total] = i
        return maxlen
            
