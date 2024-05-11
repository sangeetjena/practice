"""
Example 1:

Input: s = "babad"
Output: "bab"
Explanation: "aba" is also a valid answer.
Example 2:

Input: s = "cbbd"
Output: "bb"
"""


class Solution:
    def longestPalindrome(self, s: str) -> str:
        dp = [["" for i in range(0, len(s) + 1)] for i in range(0, len(s) + 1)]
        s1 = ""
        for i in reversed(range(len(s))):
            s1 += s[i]
        for i in range(1, len(s) + 1):
            for j in range(1, len(s) + 1):
                if s[i - 1] == s1[j - 1]:
                    dp[i][j] = s[i - 1] + dp[i - 1][j - 1]
                else:
                    dp[i][j] = dp[i - 1][j] if len(dp[i - 1][j]) > len(dp[i][j - 1]) else dp[i][j - 1]

        return dp[-1][-1]