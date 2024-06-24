"""
https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/
"""

class Solution:
    def findDisappearedNumbers(self, nums: List[int]) -> List[int]:
        missingNums = []
        for i in range(len(nums)):
            if nums[abs(nums[i])-1] >0 :
                # print(abs(nums[i])-1, nums[abs(nums[i])-1])
                nums[abs(nums[i])-1] = nums[abs(nums[i])-1] * -1
        for i in range(len(nums)):
            if nums[i] >0:
                missingNums.append(i+1)
        # print(nums)
        return missingNums


        
