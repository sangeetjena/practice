"""
https://leetcode.com/problems/3sum-closest/description/

Given an integer array nums of length n and an integer target, find three integers in nums such that the sum is closest to target.

Return the sum of the three integers.

You may assume that each input would have exactly one solution.

 

Example 1:

Input: nums = [-1,2,1,-4], target = 1
Output: 2
Explanation: The sum that is closest to the target is 2. (-1 + 2 + 1 = 2).
Example 2:

Input: nums = [0,0,0], target = 1
Output: 0
Explanation: The sum that is closest to the target is 0. (0 + 0 + 0 = 0).

Note:
similar to trangle problem
"""

class Solution:
    def threeSumClosest(self, nums: List[int], target: int) -> int:
        nums=sorted(nums)

        print(nums)
        prev = 99999
        for i in range(len(nums)):
            l, r = i+1, len(nums)-1
            while l<r:
                res = nums[i] + nums[l] + nums[r]
                if abs(res - target) < abs(prev - target):
                    prev = res
                if res > target:
                    r-=1
                elif res < target:
                    l+=1
                else:
                    return res
        return prev
