"""
https://leetcode.com/problems/palindromic-substrings/

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
        
