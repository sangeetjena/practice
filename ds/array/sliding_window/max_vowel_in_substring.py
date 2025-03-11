"""
https://leetcode.com/problems/maximum-number-of-vowels-in-a-substring-of-given-length/?envType=study-plan-v2&envId=leetcode-75

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
        
