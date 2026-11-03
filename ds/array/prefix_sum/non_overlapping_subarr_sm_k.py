"""
https://leetcode.com/problems/maximum-number-of-non-overlapping-subarrays-with-sum-equals-target/description/
Given an array nums and an integer target, return the maximum number of non-empty non-overlapping subarrays such that the sum of values in each subarray is equal to target.

 

Example 1:

Input: nums = [1,1,1,1,1], target = 2
Output: 2
Explanation: There are 2 non-overlapping subarrays [1,1,1,1,1] with sum equals to target(2).
Example 2:

Input: nums = [-1,3,5,1,4,2,-9], target = 6
Output: 2
Explanation: There are 3 subarrays with sum equal to 6.
([5,1], [4,2], [3,5,1,4,2,-9]) but only the first 2 are non-overlapping.

Note: one i find an sub array sum equals to k i will reset prefix sum and total sum value, as i want to find non overlapping subarray 

"""

class Solution:
    def maxNonOverlapping(self, nums: list[int], target: int) -> int:
        prefix =  defaultdict(int)
        prefix[0] = 1
        total = 0
        count = 0
        for i in range(len(nums)):
            total+=nums[i]
            if total-target in prefix:
                count+=1
                prefix = {0:i}
                total = 0
            prefix[total] = i
        return count
        
