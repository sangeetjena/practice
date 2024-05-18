"""
https://leetcode.com/problems/number-of-dice-rolls-with-target-sum/
https://www.youtube.com/watch?v=hfUxjdjVQN4&t=1s
"""
class Solution:
    def numRollsToTarget(self, n: int, k: int, target: int) -> int:
        mod = 10**9+7
        dp = [0 for _ in range(target+1)]
        dp[0] = 1
        for dice in range(1, n+1):
            next_dp  = [0 for _ in range(target+1)]
            for val in range(1, k+1):
                for tgt in range(val, target+1):
                    next_dp[tgt] = (next_dp[tgt] + dp[tgt-val])%mod
            dp = next_dp
        return dp[target]