"""
https://leetcode.com/problems/koko-eating-bananas/description/

Note: simple logic is to increase k value from 1 to max(piles) but to optimize lenier search use binary search.
"""

class Solution:
    def minEatingSpeed(self, piles: List[int], h: int) -> int:
        mx = max(piles)
        sm = sum(piles)
        l = 1
        r = mx
        while l<r:
            mid = (l+r)//2
            cnt = 0
            for elem in piles:
                cnt+= math.ceil(elem/mid)
            print(sm,mx,cnt, mid)
            if cnt>h:
                # this we know fo sure with this mid we cna't eat all banana so increase the mid+1
                l=mid+1
            else:
                # why mind not mid-1, we know form above if that with the mid we were abel to eat all banana but what if this is the min mid value.
                # or take a min value check always the min value when we able to eat all banana.
                r=mid
        return l
