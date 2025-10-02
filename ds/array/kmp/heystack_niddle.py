"""
https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/description/

Given two strings needle and haystack, return the index of the first occurrence of needle in haystack, or -1 if needle is not part of haystack.

 

Example 1:

Input: haystack = "sadbutsad", needle = "sad"
Output: 0
Explanation: "sad" occurs at index 0 and 6.
The first occurrence is at index 0, so we return 0.
Example 2:

Input: haystack = "leetcode", needle = "leeto"
Output: -1
Explanation: "leeto" did not occur in "leetcode", so we return -1.

Note: find freqency of letter and check if all charector match with 1srt string.
"""

class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        w = len(needle)-1
        s = 0
        for i in range(len(haystack)+1):
            if haystack[s:i] == needle:
                return s
            if len(haystack[s:i])> w:
                s+=1
        return -1



        
