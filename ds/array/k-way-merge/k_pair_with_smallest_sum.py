"""
https://leetcode.com/problems/find-k-pairs-with-smallest-sums/description/
You are given two integer arrays nums1 and nums2 sorted in non-decreasing order and an integer k.

Define a pair (u, v) which consists of one element from the first array and one element from the second array.

Return the k pairs (u1, v1), (u2, v2), ..., (uk, vk) with the smallest sums.

 

Example 1:

Input: nums1 = [1,7,11], nums2 = [2,4,6], k = 3
Output: [[1,2],[1,4],[1,6]]
Explanation: The first 3 pairs are returned from the sequence: [1,2],[1,4],[1,6],[7,2],[7,4],[11,2],[7,6],[11,4],[11,6]
Example 2:

Input: nums1 = [1,1,2], nums2 = [1,2,3], k = 2
Output: [[1,1],[1,1]]
Explanation: The first 2 pairs are returned from the sequence: [1,1],[1,1],[1,2],[2,1],[1,2],[2,2],[1,3],[1,3],[2,3]

 
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
        
