"""
https://leetcode.com/problems/coin-change/description/

Note: similar to coin 1 problem, but need to find no of all possible combination
also need to take coins first and then amount.

"""
class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        dp = [float('inf') for i in range(amount+1)]
        dp[0] = 0
        for i in range(1,amount+1):
            for j in coins:
                if j<= i:
                    # if not taking the value then take value at same position 
                    # if taken then 1+ value of remaining waight.
                    dp[i] = min(dp[i], 1 + dp[i-j] )
        return -1 if dp[-1]==float('inf') else dp[-1]
        
