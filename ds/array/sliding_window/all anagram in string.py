"""
https://leetcode.com/problems/find-all-anagrams-in-a-string/description/

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
