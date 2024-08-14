"""
https://leetcode.com/problems/find-k-closest-elements/

NOte: can be solved in multiple other approches as weel [https://leetcode.com/problems/find-k-closest-elements/solutions/5370196/four-approaches-with-explanations/]

Given a sorted integer array arr, two integers k and x, return the k closest integers to x in the array. The result should also be sorted in ascending order.

An integer a is closer to x than an integer b if:

|a - x| < |b - x|, or
|a - x| == |b - x| and a < b
 

Example 1:

Input: arr = [1,2,3,4,5], k = 4, x = 3
Output: [1,2,3,4]
Example 2:

Input: arr = [1,2,3,4,5], k = 4, x = -1
Output: [1,2,3,4]
"""
class Solution:
    def findClosestElements(self, arr: List[int], k: int, x: int) -> List[int]:
        import heapq
        lst = [(abs(x-elem),elem) for elem in arr]
        out = []
        heapq.heapify(lst)
        for i in range(k):
            out.append(heapq.heappop(lst)[1])
        return sorted(out)

        
