"""
https://leetcode.com/problems/longest-palindromic-subsequence/

Note: similar to LCS

"""
class Solution:
    def longestPalindromeSubseq(self, s: str) -> int:
        # reverse the string and find longest common subsequence == longest palindromic subsequence.
        s1 = s[::-1]
        dp = [[0 for _ in range(len(s)+1)] for _ in range(len(s)+1)]
        for i in range(1, len(s)+1):
            for j in range(1, len(s)+1):
                # if matching then 1 + count of lcs before current index.
                if s[i-1] == s1[j-1]:
                    dp[i][j] = 1+ dp[i-1][j-1]
                else:
                # other wide maximum of previous index of s or s1
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        return dp[-1][-1]
        
