"""
https://leetcode.com/problems/maximum-earnings-from-taxi/description/


Note: this solution has issue with memory limit exceed exception
"""
class Solution:
    def maxTaxiEarnings(self, n: int, rides: List[List[int]]) -> int:
        dp = [[0 for i in range(n+1)] for _ in range(len(rides)+1)]
        rides = sorted(rides)
        for i in range(1,len(rides)+1):
            for j in range(n+1):
                wt = rides[i-1][1] - rides[i-1][0]
                if (rides[i-1][1]) <= j:
                    dp[i][j] = max( dp[i-1][j], rides[i-1][2] + wt +  dp[i-1][rides[i-1][0]])
                else:
                    dp[i][j] = dp[i-1][j]
        return dp[-1][-1]
