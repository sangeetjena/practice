"""
https://leetcode.com/problems/longest-palindromic-subsequence/

Note: similar to LCS

"""
class Solution:
    def longestPalindromeSubseq(self, s: str) -> int:
        s1 = s[::-1]
        if s1==s:
            return len(s)
        dp = [[0 for _ in range(len(s)+1)] for _ in range(len(s)+1)]
        for i in range(1, len(s)+1):
            for j in range(1, len(s)+1):
                if s[i-1] == s1[j-1]:
                    dp[i][j] = 1+ dp[i-1][j-1]
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        return dp[-1][-1]
        
        
