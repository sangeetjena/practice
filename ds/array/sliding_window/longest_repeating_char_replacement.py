"""
https://leetcode.com/problems/longest-repeating-character-replacement/description/
https://www.youtube.com/watch?v=gqXU1UyA8pk&t=288s

You are given a string s and an integer k. You can choose any character of the string and change it to any other uppercase English character. You can perform this operation at most k times.

Return the length of the longest substring containing the same letter you can get after performing the above operations.

 

Example 1:

Input: s = "ABAB", k = 2
Output: 4
Explanation: Replace the two 'A's with two 'B's or vice versa.

Note: i will use a window and keep count of frequency of number , then leaving the highest frequency number if sum of rest of the frequency < k then it is a vaid window .,
take max of prev window with current window. else increase the starting of window and recude the frequency.
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
