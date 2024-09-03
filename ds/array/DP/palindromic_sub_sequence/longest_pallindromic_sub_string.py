"""
https://leetcode.com/problems/longest-palindromic-substring/
https://www.youtube.com/watch?v=XYQecbcd6_c
"""
Approach1:
=============




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
            # for odd length
            while l>=0 and r<len(s) and s[l]==s[r]:
                templen = r-l
                if templen > maxlen:
                    val = s[l:r+1]
                    maxlen = templen
                l-=1
                r+=1
            l,r = i, i+1
            templen=0
            # for even length substring.
            while l>=0 and r<len(s) and s[l] == s[r]:
                templen = r-l
                if templen > maxlen:
                    val = s[l:r+1]
                    maxlen = templen
                l-=1
                r+=1
        return val

        
