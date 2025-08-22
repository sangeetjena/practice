"""
https://leetcode.com/problems/coin-change/description/

You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money.

Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1.

You may assume that you have an infinite number of each kind of coin.

 

Example 1:

Input: coins = [1,2,5], amount = 11
Output: 3
Explanation: 11 = 5 + 5 + 1
Example 2:

Input: coins = [2], amount = 3
Output: -1
Example 3:

Input: coins = [1], amount = 0
Output: 0

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
        
