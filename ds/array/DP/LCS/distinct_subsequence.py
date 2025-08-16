"""
https://leetcode.com/problems/distinct-subsequences/
https://www.youtube.com/watch?v=-RDzMJ33nx8

Given two strings s and t, return the number of distinct subsequences of s which equals t.

The test cases are generated so that the answer fits on a 32-bit signed integer.

 

Example 1:

Input: s = "rabbbit", t = "rabbit"
Output: 3
Explanation:
As shown below, there are 3 ways you can generate "rabbit" from s.
rabbbit
rabbbit
rabbbit
Example 2:

Input: s = "babgbag", t = "bag"
Output: 5
Explanation:
As shown below, there are 5 ways you can generate "bag" from s.
babgbag
babgbag
babgbag
babgbag
babgbag


Note: similar to LCS, but insteed of max(), do  (+)
"""

class Solution:
    def numDistinct(self, s: str, t: str) -> int:
        n, m = len(s), len(t)
        dp = [[0.0] * (m + 1) for _ in range(n + 1)]

        for i in range(n + 1):
            dp[i][0] = 1.0

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if s[i - 1] == t[j - 1]:
                    # why no dp[i][j-1]: because we cant leave any element from 2nd word. so we can't leave any letter form 2nd word
                    dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]
                else:
                    dp[i][j] = dp[i - 1][j]

        return int(dp[n][m])
