"""
https://leetcode.com/problems/house-robber/

Note: similar to min cost climb but difference is you can't theft adjacent value so, presnt index cost can be added to i-2 index value.

"""
class Solution:
    def rob(self, nums: List[int]) -> int:
        nums = [0] + nums
        for i in range(2,len(nums)):
            nums[i] = max(nums[i-1], nums[i]+nums[i-2])
        return nums[-1]
        
