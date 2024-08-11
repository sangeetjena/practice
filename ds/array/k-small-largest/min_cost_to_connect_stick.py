"""
Note: it is not same as min coin to form target problem, as here always need to take two least min element to form a num.
this can be solved by sorting array and find min but sorting will take time so use min heap.

https://leetcode.com/problems/minimum-cost-to-connect-sticks/description/

You have some number of sticks with positive integer lengths. These lengths are given as an array sticks, where sticks[i] is the length of the ith stick.

You can connect any two sticks of lengths x and y into one stick by paying a cost of x + y. You must connect all the sticks until there is only one stick remaining.

Return the minimum cost of connecting all the given sticks into one stick in this way.

 

Example 1:

Input: sticks = [2,4,3]
Output: 14
Explanation: You start with sticks = [2,4,3].
1. Combine sticks 2 and 3 for a cost of 2 + 3 = 5. Now you have sticks = [5,4].
2. Combine sticks 5 and 4 for a cost of 5 + 4 = 9. Now you have sticks = [9].
There is only one stick left, so you are done. The total cost is 5 + 9 = 14.


"""
class Solution:
    def connectSticks(self, sticks: List[int]) -> int:
        import heapq
        heapq.heapify(sticks)
        totalcost = 0
        while len(sticks)>1:
            # take 1st two smallest element and find sum , then add it to total and push it back to heap.
            firstnum = heapq.heappop(sticks)
            secondnum = heapq.heappop(sticks)
            sm = firstnum + secondnum
            totalcost = totalcost + sm
            heapq.heappush(sticks, sm)
        return totalcost
        
