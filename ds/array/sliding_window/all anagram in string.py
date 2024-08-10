"""
https://leetcode.com/problems/find-all-anagrams-in-a-string/description/

Note: find count of all charector in the one string and check if the window you are taking in other string , char count exactly match with the other strin, then it is an anagram.

Given two strings s and p, return an array of all the start indices of p's anagrams in s. You may return the answer in any order.

An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.

 

Example 1:

Input: s = "cbaebabacd", p = "abc"
Output: [0,6]
Explanation:
The substring with start index = 0 is "cba", which is an anagram of "abc".
The substring with start index = 6 is "bac", which is an anagram of "abc".

"""

class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        dp = {}
        for item in p:
            if item in dp.keys():
                dp[item]+=1
            else:
                dp[item]=1
        start = end =0
        pos= []
        while end < len(s):
            if s[end] in dp.keys():
                dp[s[end]]-=1
            if (end-start+1) > len(p):
                if s[start] in dp.keys():
                    dp[s[start]]+=1
                start+=1 
            if all(value==0 for value in dp.values()):
                pos.append(start)
            end+=1
        return pos
