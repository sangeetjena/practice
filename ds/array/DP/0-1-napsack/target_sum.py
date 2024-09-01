"""
https://leetcode.com/problems/target-sum/

Note: it is similar to subset sum = k, we need to devide nums to two sets one +ve and one -ve.
sum1 - sum2 = target # sum2 of -ve nos
sum1 - (totalsum -sum1) = target
2sum1 - totalum = target
sum1 = (target + totalsum) /2
now the problem became subset sum equals to sum1
"""
class Solution:
    def findTargetSumWays(self, nums: List[int], target: int) -> int:
        total = sum(nums)
        # if i have only one element and that one element match to target then there is only one way i canform the target
        if len(nums) == 1:
            return 1 if (nums[0] == target) or (-nums[0] == target) else 0
        if (total+target)%2 != 0:
            return 0
        # if i have all +ve no and sum is  < target value then we can't build partition in any way.
        if abs(target)> total:
            return 0
        sm1 = (total+target)//2
        
        dp = [[0 for i in range(sm1+1)] for j in range(len(nums)+1)]
        dp[0][0]=1
        for i in range(1,len(nums)+1):
            for j in range(sm1+1):
                if nums[i-1] <= j:
                    dp[i][j]= dp[i-1][j] + dp[i-1][j-nums[i-1]]
                else:
                    dp[i][j] = dp[i-1][j]
        print(dp)
        return dp[-1][-1]
