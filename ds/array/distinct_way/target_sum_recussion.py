"""
https://leetcode.com/problems/target-sum/description/
https://www.youtube.com/watch?v=g0npyaQtAQM
"""
class Solution:
    def findTargetSumWays(self, nums: List[int], target: int) -> int:
        dp = {}
        def targetSum(i, target):
            if (i == 0):
                return 1 if target == 0 else 0
            if (i, target) in dp:
                return dp[(i, target)]
            dp[(i, target)] = targetSum(i-1, target + nums[i-1]) + targetSum(i-1, target - nums[i-1])
            return dp[(i,target)]
        return targetSum(len(nums), target)
        
             
        
