"""
https://leetcode.com/problems/maximum-number-of-vowels-in-a-substring-of-given-length/?envType=study-plan-v2&envId=leetcode-75

Given a string s and an integer k, return the maximum number of vowel letters in any substring of s with length k.

Vowel letters in English are 'a', 'e', 'i', 'o', and 'u'.

 

Example 1:

Input: s = "abciiidef", k = 3
Output: 3
Explanation: The substring "iii" contains 3 vowel letters.
Example 2:

Input: s = "aeiou", k = 2
Output: 2
Explanation: Any substring of length 2 contains 2 vowels.
Example 3:

Input: s = "leetcode", k = 3
Output: 2
Explanation: "lee", "eet" and "ode" contain 2 vowels.

Note: sliding window problem, take curr counter, increment it if found a vowel and decrement if the window size exceed and start index value is a vowel.

"""
class Solution:
    def maxVowels(self, s: str, k: int) -> int:
        vow = ['a','e','i','o','u']
        start, end = 0,0
        max_count = 0
        curr_vow = 0
        while end < len(s):
            if end - start <= k-1:
                if s[end] in vow:
                    curr_vow +=1
                    max_count = max(max_count, curr_vow)
                end+=1
            else:
                if s[start] in vow:
                    curr_vow-=1
                start+=1
        return max_count
        
