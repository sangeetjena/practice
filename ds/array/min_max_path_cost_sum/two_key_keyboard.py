"""
https://leetcode.com/problems/2-keys-keyboard/
"""


class Solution:
    def minSteps(self, n: int) -> int:
        dp = {}
        dp[0] = 0
        dp[1] = 0
        dp[2] = 2
        dp[3] = 3
        if n < 4:
            return dp[n]
        for i in range(4, n + 1):
            dp[i] = i
            for j in range(2, n + 1):
                # if n%j is odd then we need n no of steps
                # which we cover in the above step
                if (i % j == 0):
                    # chcking if we can create group of 2, 3, 4, ..n elemnet.
                    # then checking how many step it took to create that group.
                    dp[i] = min(dp[i], dp[int(i / j)] + j)
        return dp[n]
