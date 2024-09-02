"""
https://leetcode.com/problems/fibonacci-number/description/

"""

class Solution:
    def fib(self, n: int) -> int:
        dp = [0]*n
        if n==0:
            return 0
        if n<3:
            return 1
        dp[0]=1
        dp[1]=1
        for i in range(2,n):
            dp[i] = dp[i-1]+dp[i-2]
        return dp[-1]
