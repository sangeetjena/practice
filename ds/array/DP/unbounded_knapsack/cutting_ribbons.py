"""
https://leetcode.com/problems/cutting-ribbons/description/
Note: simple solution is to increment k value from 1 to max(ribbons) but to optimise lienear search use binary search

"""

class Solution:
    def maxLength(self, ribbons: List[int], k: int) -> int:
        mx = max(ribbons)
        l=1
        r=mx
        while l<=r:
            mid = (l+r)//2
            cnt = 0
            for rib in ribbons:
                cnt+= math.floor(rib/mid)
            print(l,r,mid,cnt)
            if cnt<k:
                r=mid-1
            else:
                l = mid+1
        return r
