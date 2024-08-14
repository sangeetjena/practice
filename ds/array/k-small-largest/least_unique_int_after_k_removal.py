"""
https://leetcode.com/problems/least-number-of-unique-integers-after-k-removals/description/

Given an array of integers arr and an integer k. Find the least number of unique integers after removing exactly k elements.

 

Example 1:

Input: arr = [5,5,4], k = 1
Output: 1
Explanation: Remove the single 4, only 5 is left.
Example 2:
Input: arr = [4,3,1,1,3,3,2], k = 3
Output: 2
Explanation: Remove 4, 2 and either one of the two 1s or three 3s. 1 and 3 will be left.


"""
class Solution:
    def findLeastNumOfUniqueInts(self, arr: List[int], k: int) -> int:
        heapq
        dct = {}
        # 1st find the frequency of elements
        for x in arr:
            if x in dct.keys():
                dct[x]+=1
            else:
                dct[x] = 1
        lst = [(dct[key],key) for key in dct.keys()]
        heapq.heapify(lst)
        count = 0
        for i in range(k):
        # keep poping elements which has lower frequency and reduce the count value 
        # if count value > k then add remaining count and push it back to heap 
        # find no of element left in the list , that will be the min number of elements
            cnt, elem = heapq.heappop(lst)
            count+=cnt
            if count == k:
                break
            if count >k:
                heapq.heappush(lst, (count-k, elem))
        return len(lst)
