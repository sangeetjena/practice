"""
https://leetcode.com/problems/climbing-stairs/
"""


class Solution:
    def climbStairs(self, n: int) -> int:
        dp = [0 for _ in range(n + 1)]
        dp[1] = 1
        dp[0] = 1
        max_step = 2
        for i in range(2, n + 1):
            for j in range(1, max_step + 1):
                dp[i] += dp[i - j]
        print(dp)
        return dp[-1]

