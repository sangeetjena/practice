"""
https://leetcode.com/problems/perfect-squares/description/
"""


class Solution:
    def numSquares(self, n: int) -> int:
        psq = [i * i for i in range(n + 1) if i * i <= n]
        dp = [9999 for i in range(n + 1)]
        dp[0] = 0
        print(psq)
        for i in range(n + 1):
            for j in psq:
                if (j > i):
                    continue
                dp[i] = min(dp[i], 1 + dp[i - j])
        print(dp)
        return dp[-1]

