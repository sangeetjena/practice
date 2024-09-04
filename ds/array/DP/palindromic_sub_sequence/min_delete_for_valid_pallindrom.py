"""
https://leetcode.com/problems/valid-palindrome-iii/description/

Note:
find longest pallindromic subsequence then find the difference between length of stiring to lps, that will be min delete needed to make the string pallindrom.
"""

class Solution:
    def isValidPalindrome(self, s: str, k: int) -> bool:
        s1 = s[::-1]
        dp = [[0 for _ in range(len(s)+1)] for _ in range(len(s)+1)]
        for i in range(1,len(s)+1):
            for j in range(1, len(s)+1):
                if s[i-1] == s1[j-1]:
                    dp[i][j] = 1+dp[i-1][j-1]
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        return k>= len(s)-dp[-1][-1]
        
