"""
https://leetcode.com/problems/longest-palindromic-substring/
2pointer: https://www.youtube.com/watch?v=XYQecbcd6_c
dp: https://www.youtube.com/watch?v=UflHuQj6MVA
"""
Approach1:
=============
dp implementation: https://www.youtube.com/watch?v=UflHuQj6MVA

class Solution:
    def longestPalindrome(self, s: str) -> str:
        lps = ""
        dp = [[False for i in range(len(s)+1)] for x in range(len(s)+1)]
        for e in range(1, len(s)+1):
            dp[e][e] = True
            for st in range(e):
                if s[st-1] == s[e-1] and (e-st<=1 or dp[st+1][e-1]):
                    print(st, e, s[st-1], s[e-1])
                    lps = max(lps, s[st-1: e])
                    print(lps)
                    dp[st][e] = True

        print(dp)
        return lps

Approach2: (using pointer)
===========================
we will keep 2pointer at center and keep expanding the pointer to left and right:

class Solution:
    def longestPalindrome(self, s: str) -> str:
        maxlen = -1
        if len(s)<2:
            return s
        val = ""
        for i in range(len(s)):
            l=r=i
            templen=0
            # for odd length pallindrom
            while l>=0 and r<len(s) and s[l]==s[r]:
                templen = r-l
                if templen > maxlen:
                    val = s[l:r+1]
                    maxlen = templen
                l-=1
                r+=1
            l,r = i, i+1
            templen=0
            # for even length pallindrom.
            while l>=0 and r<len(s) and s[l] == s[r]:
                templen = r-l
                if templen > maxlen:
                    val = s[l:r+1]
                    maxlen = templen
                l-=1
                r+=1
        return val

        
