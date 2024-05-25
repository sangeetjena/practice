"""
this can be solved using hash map and sliding window.
https://leetcode.com/problems/longest-substring-without-repeating-characters/solutions/1499836/C++-Sliding-Window-(+-Cheat-Sheet)/
"""
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        if(len(s) == 0):
            return 0
        i=0
        j=1
        maxlen =1
        while j< len(s) and i<j:
            if s[j] not in s[i:j]:
                if maxlen < len(s[i:j+1]):
                    maxlen =len(s[i:j+1])
                j+=1
                continue
            else:
                i+=1
                # to handle condition when i == j, to prevent the outer while loop to break.
                if i == j:
                    j+=1
        return maxlen

        
