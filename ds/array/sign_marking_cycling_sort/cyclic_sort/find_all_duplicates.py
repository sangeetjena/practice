"""
https://leetcode.com/problems/find-all-duplicates-in-an-array/submissions/1298299107/
"""

class Solution:
    def findDuplicates(self, nums: List[int]) -> List[int]:
        dups = []
        for i in range(len(nums)):
            if nums[abs(nums[i])-1]<0:
                dups.append(abs(nums[i]))
            else:
                nums[abs(nums[i])-1] = nums[abs(nums[i])-1] *-1
        return dups
        
