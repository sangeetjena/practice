"""
https://leetcode.com/problems/maximum-width-ramp/description/

A ramp in an integer array nums is a pair (i, j) for which i < j and nums[i] <= nums[j]. The width of such a ramp is j - i.

Given an integer array nums, return the maximum width of a ramp in nums. If there is no ramp in nums, return 0.

 

Example 1:

Input: nums = [6,0,8,2,1,5]
Output: 4
Explanation: The maximum width ramp is achieved at (i, j) = (1, 5): nums[1] = 0 and nums[5] = 5.
Example 2:

Input: nums = [9,8,1,0,1,9,4,0,4,1]
Output: 7
Explanation: The maximum width ramp is achieved at (i, j) = (2, 9): nums[2] = 1 and nums[9] = 1.

Note: 
it is similar to the hot days ahead problem but diffrence is that after getting larger value to it right we should not stop and keep moving forward. 
so at each point caclulate the larger vaue to the righ and check all point to the right and if we find right has larger value then we keep moving he right pointer and taking max len.
only move left pointer if right pointer max right value is lesser than left.

"""
class Solution:
    def maxWidthRamp(self, nums: list[int]) -> int:
        maxright = [nums[i] for i in range(len(nums))]
        total = 0
        for i in reversed(range(len(nums))):
            if i == len(nums)-1:
                continue
            maxright[i] = max(nums[i], maxright[i+1])
        i,j = 0,0
        while i<=j and j<len(nums):
            if nums[i] <= maxright[j]:
                total = max(total, j-i)
                j+=1
            else:
                i+=1
        return total


