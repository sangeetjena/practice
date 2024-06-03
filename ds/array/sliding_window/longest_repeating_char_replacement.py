"""
https://leetcode.com/problems/longest-repeating-character-replacement/description/
https://www.youtube.com/watch?v=gqXU1UyA8pk&t=288s
"""

class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        window = 0
        maxlen = 0
        start, end =0,0
        dp = {}
        while end < len(s):
            if s[end] not in dp.keys():
                dp[s[end]] = 1
            else:
                dp[s[end]] +=1
            window +=1
            # replace character if not of challeter leaving max occurance character is greater than k
            while window - max(dp.values()) > k:
                dp[s[start]]-=1
                start+=1
                window-=1
            maxlen = max(maxlen, window)
            end+=1
            print(maxlen)
        return maxlen
