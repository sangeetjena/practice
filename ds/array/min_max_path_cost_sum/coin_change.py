"""
https://leetcode.com/problems/coin-change/
"""

class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        if amount == 0:
            return 0
        dp = [9999 for i in range(amount + 1)]
        dp[0] = 0
        for i in range(amount + 1):
            for j in range(len(coins)):
                if (coins[j] <= i):
                    dp[i] = min(dp[i], 1 + dp[i - coins[j]])
                print(dp)
        if dp[-1] == 9999:
            return -1
        return dp[-1]


