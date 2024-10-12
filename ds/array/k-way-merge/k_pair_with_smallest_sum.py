"""
https://leetcode.com/problems/find-k-pairs-with-smallest-sums/description/
Note: add all combination with 1st array then pop smallest element and keep adding next element from next array
"""
import heapq
class Solution:
    def kSmallestPairs(self, nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
        sums = []
        temp = []
        for i in range(len(nums1)):
            heapq.heappush(temp,(nums1[i] + nums2[0], i,0))
        print(temp)
        while k>0 and len(temp)>0:
            sm,n1,n2 = heapq.heappop(temp)
            sums.append([nums1[n1], nums2[n2]])
            print(n1,n2, len(nums2))
            k-=1
            if len(nums2)<= n2+1:
                continue
            heapq.heappush(temp,(nums1[n1] + nums2[n2+1], n1,n2+1))
        return sums
        
