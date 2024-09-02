"""
https://leetcode.com/problems/coin-change/description/

Note: similar to coin 1 problem, but need to find no of all possible combination
also need to take coins first and then amount.

"""
class Solution:
    def change(self, amount: int, coins: List[int]) -> int:
        dp = [0 for _ in range(amount+1)]
        dp[0] = 1
        for coin in coins:
            for j in range(coin, amount+1):
                dp[j] += dp[j-coin]
        return dp[-1]
        
        
