"""
https://leetcode.com/problems/palindromic-substrings/

https://www.youtube.com/watch?v=4RACzI5-du8

Given a string s, return the number of palindromic substrings in it.

A string is a palindrome when it reads the same backward as forward.

A substring is a contiguous sequence of characters within the string.

Example 1:

Input: s = "abc"
Output: 3
Explanation: Three palindromic strings: "a", "b", "c".
Example 2:

Input: s = "aaa"
Output: 6
Explanation: Six palindromic strings: "a", "a", "a", "aa", "aa", "aaa".

Note: ( it is pallindromic sub string not subsequence)
bruite force: at each i position expand search to left and righ side.
case 1: even size pallindrom where l == r
case 2: odd size pallindrom, where at middle there will be a common character and i-1 == i+1.

DP: 
"""
class Solution:
    def countSubstrings(self, s: str) -> int:
        cnt=0
        for i in range(len(s)):
            l=i
            r=i+1
            # count all odd size pallindrom
            while l>=0 and r<len(s) and s[l]==s[r]:
                cnt+=1
                l-=1
                r+=1
            l=r=i
            # count all even size pallindrom
            while l>=0 and r<len(s) and s[l]==s[r]:
                cnt+=1
                l-=1
                r+=1
        return cnt
        
