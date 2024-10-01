"""
https://leetcode.com/problems/minimum-insertion-steps-to-make-a-string-palindrome/description/

Note: same as not of deletion to make a string palindrom.

"""

class Solution:
    def minInsertions(self, s: str) -> int:
        dp = [[0 for i in range(len(s)+1)] for i in range(len(s)+1)]
        s1 = s[::-1]
        print(s, s1)
        for i in range(1,len(s)+1):
            for j in range(1,len(s)+1):
                if s[i-1] == s1[j-1]:
                    dp[i][j] = 1+ dp[i-1][j-1]
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        print(dp)
        return len(s) - dp[-1][-1]


        
