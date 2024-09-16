"""
https://leetcode.com/problems/roman-to-integer/

Note: if lower value come before higher value consider it as negerive.
"""

class Solution:
    def romanToInt(self, s: str) -> int:
        dct = {'I':1,
                'V':5,
                'X':10,
                'L':50,
                'C':100,
                'D':500,
                'M':1000
                }
        total = 0
        for i in range(len(s)-1):
            if dct[s[i]] < dct[s[i+1]]:
                total-=dct[s[i]]
            else:
                total+=dct[s[i]]
        total+=dct[s[-1]]
        return total

        
