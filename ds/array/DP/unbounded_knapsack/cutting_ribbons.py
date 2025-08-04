"""
https://leetcode.com/problems/cutting-ribbons/description/

You are given an integer array ribbons, where ribbons[i] represents the length of the ith ribbon, and an integer k. You may cut any of the ribbons into any number of segments of positive integer lengths, or perform no cuts at all.

For example, if you have a ribbon of length 4, you can:
Keep the ribbon of length 4,
Cut it into one ribbon of length 3 and one ribbon of length 1,
Cut it into two ribbons of length 2,
Cut it into one ribbon of length 2 and two ribbons of length 1, or
Cut it into four ribbons of length 1.
Your task is to determine the maximum length of ribbon, x, that allows you to cut at least k ribbons, each of length x. You can discard any leftover ribbon from the cuts. If it is impossible to cut k ribbons of the same length, return 0.

 

Example 1:

Input: ribbons = [9,7,5], k = 3
Output: 5
Explanation:
- Cut the first ribbon to two ribbons, one of length 5 and one of length 4.
- Cut the second ribbon to two ribbons, one of length 5 and one of length 2.
- Keep the third ribbon as it is.
Now you have 3 ribbons of length 5.

Note: simple solution is to increment k value from 1 to max(ribbons) but to optimise lienear search use binary search. 
it is not needed to cut all the ribbon. it should produce minimum, k ribbon after cut. 

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
