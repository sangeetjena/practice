"""
https://leetcode.com/problems/first-missing-positive/description/
"""

class Solution:
    def firstMissingPositive(self, nums: List[int]) -> int:
        # convert all negative number out of bound or not include in calculation
        for i in range(len(nums)):
            # discard 0's from calculation
            if nums[i] <=0:
                nums[i] = len(nums)+1
        for i in range(len(nums)):
            if abs(nums[i])> len(nums):
                continue
            if nums[abs(nums[i])-1] >0:
                nums[abs(nums[i])-1] = nums[abs(nums[i])-1]*-1
        print(nums)
        for i in range(len(nums)):
            if nums[i]>=0:
                return i+1
        return len(nums)+1
        
