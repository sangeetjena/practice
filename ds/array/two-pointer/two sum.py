"""
https://leetcode.com/problems/two-sum/description/
Note: using hash table, similar to prefix sum
"""

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        dp = {}
        for i in range(0,len(nums)):
            if target - nums[i] in dp.keys():
                return [dp[target - nums[i]], i]
            dp[nums[i]] = i
        return []


======== two pointer approch ======
# sort the list and keep one pointer at end and one at begining
# if sum is less then move the left else right 
# break the loop if element found 
