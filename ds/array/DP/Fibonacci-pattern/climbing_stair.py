"""

"""
class Solution:
    def climbStairs(self, n: int) -> int:
        dp = [0]*n
        if n<2:
            return 1
        dp[0] = 1
        dp[1] = 2
        for i in range(2, n):
            # one can reach from previous 2 step or previous one step so add both.
            dp[i] = dp[i-2]+dp[i-1]
        return dp[-1]
