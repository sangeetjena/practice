"""
https://leetcode.com/problems/happy-number/
https://www.youtube.com/watch?v=ljz85bxOYJ0
"""
class Solution:
    def isHappy(self, n: int) -> bool:
        dp={}
        while n!=1:
            out=0
            while n:
                digit = n%10
                out+=digit*digit
                n=n//10
            n=out
            print(n)
            if dp.get(out, False):
                if out == 1:
                    return True
                else:
                    return False
            else:
                dp[out]= 1
        return True
