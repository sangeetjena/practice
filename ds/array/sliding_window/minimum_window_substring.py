"""
https://leetcode.com/problems/minimum-window-substring/description/

Given two strings s and t of lengths m and n respectively, return the minimum window 
substring
 of s such that every character in t (including duplicates) is included in the window. If there is no such substring, return the empty string "".

The testcases will be generated such that the answer is unique.

 

Example 1:

Input: s = "ADOBECODEBANC", t = "ABC"
Output: "BANC"
Explanation: The minimum window substring "BANC" includes 'A', 'B', and 'C' from string t.
"""
class Solution:
    def minWindow(self, s: str, t: str) -> str:
        dp = {}
        for val in t:
            if val not in dp.keys():
                dp[val] =1
            else:
                dp[val]+=1
        start = end = 0
        minval = s
        while end < len(s):
            if s[end] in dp.keys():
                dp[s[end]]-=1
            # when all character found reduce the window and check if still all the charactor present in the dict or not.
            
            while all(val <= 0 for val in dp.values()):
                if s[start] in dp.keys():
                    dp[s[start]]+=1
                minval = minval if len(minval) < len( s[start:end+1]) else  s[start:end+1]
                start+=1
            end+=1
        return minval if start!=0 else ""
       
