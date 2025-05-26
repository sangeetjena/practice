"""
https://leetcode.com/problems/cutting-ribbons/

Note: 
brute force: starting from smaller to larger find one length and check if using that length we can form k cuts or not.
Optimised solution: 
tick here is take the largest ribbon and check using binary search if any size(cut) in large ribbon can form cuts in rest of the ribbon and can reach the value k .
if cut is possible in rest of the ribbon then increse the left value to find larger cuts else decrease the cut value.

"""
class Solution:
    def maxLength(self, ribbons: List[int], k: int) -> int:
        # idea is the create a hash map with range form min ribbon to the max ribbon
        # then take eah ribbon and check how many ribbon of length k is posible and add count to each length
        # in the hash set
        # set = {i:0 for i in range(1,max(ribbons)+1)}
        # for ribbon in ribbons:
        #     for j in range(1,ribbon+1):
        #         val = ribbon//j
        #         set[j]+=val
        # print(set)
        # for key in reversed(range(1,max(ribbons)+1)):
        #     if set[key]>=k:
        #         return key
        # return 0
        r = max(ribbons)
        l = 1
        maxribbons = 0 
        while (l<=r):
            mid = (l+r)//2
            val = 0
            # print("searching wtih ribbon length - " + str(mid))
            for ribbon in ribbons:
                val+=ribbon//mid
                # print("ribbon {} max cut = {} , total cuts= {}".format(ribbon, ribbon//mid, val))
            if val>=k:
                maxribbons = max(maxribbons, mid)
                l = mid+1
            else:
                r= mid-1
        # print(maxribbons)
        return maxribbons
        
        
