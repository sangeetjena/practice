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
        sm1 = (total+target)//2
        # if i have all +ve no and sum is  < target value then we can't build partition in any way.
        if target> total:
            return 0
        dp = [[0 for i in range(sm1+1)] for j in range(len(nums)+1)]
        for i in range(len(nums)+1):
            for j in range(sm1+1):
                if j == 0:
                    dp[i][j]=1
                    continue
                if nums[i-1] <= j:
                    dp[i][j]= dp[i-1][j] + dp[i-1][j-nums[i-1]]
                else:
                    dp[i][j] = dp[i-1][j]
        print(dp)
        return dp[-1][-1]
        
