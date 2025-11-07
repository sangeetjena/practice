"""
this can be solved using hash map and sliding window.
https://leetcode.com/problems/longest-substring-without-repeating-characters/solutions/1499836/C++-Sliding-Window-(+-Cheat-Sheet)/

Given a string s, find the length of the longest substring without duplicate characters.

 

Example 1:

Input: s = "abcabcbb"
Output: 3
Explanation: The answer is "abc", with the length of 3. Note that "bca" and "cab" are also correct answers.
Example 2:

Input: s = "bbbbb"
Output: 1
Explanation: The answer is "b", with the length of 1.
Example 3:

Input: s = "pwwkew"
Output: 3
Explanation: The answer is "wke", with the length of 3.
Notice that the answer must be a substring, "pwke" is a subsequence and not a substring.

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

        
