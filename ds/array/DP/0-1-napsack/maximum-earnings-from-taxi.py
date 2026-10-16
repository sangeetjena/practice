"""
https://leetcode.com/problems/maximum-earnings-from-taxi/description/

There are n points on a road you are driving your taxi on. The n points on the road are labeled from 1 to n in the direction you are going, and you want to drive from point 1 to point n to make money by picking up passengers. You cannot change the direction of the taxi.

The passengers are represented by a 0-indexed 2D integer array rides, where rides[i] = [starti, endi, tipi] denotes the ith passenger requesting a ride from point starti to point endi who is willing to give a tipi dollar tip.

For each passenger i you pick up, you earn endi - starti + tipi dollars. You may only drive at most one passenger at a time.

Given n and rides, return the maximum number of dollars you can earn by picking up the passengers optimally.

Note: You may drop off a passenger and pick up a different passenger at the same point.

 

Example 1:

Input: n = 5, rides = [[2,5,4],[1,5,1]]
Output: 7
Explanation: We can pick up passenger 0 to earn 5 - 2 + 4 = 7 dollars.
Example 2:

Input: n = 20, rides = [[1,6,1],[3,10,2],[10,12,3],[11,12,2],[12,15,2],[13,18,1]]
Output: 20
Explanation: We will pick up the following passengers:
- Drive passenger 1 from point 3 to point 10 for a profit of 10 - 3 + 2 = 9 dollars.
- Drive passenger 2 from point 10 to point 12 for a profit of 12 - 10 + 3 = 5 dollars.
- Drive passenger 5 from point 13 to point 18 for a profit of 18 - 13 + 1 = 6 dollars.
We earn 9 + 5 + 6 = 20 dollars in total.


Note: this solution has issue with memory limit exceed exception
"""

# using bisect
from bisect import bisect_right
class Solution:
    def maxTaxiEarnings(self, n: int, rides: List[List[int]]) -> int:
        rides = sorted(rides, key=lambda x: x[1])
        ends = [ride[1] for ride in rides]
        dp = [0] * (len(rides)+1)
        for i in range(1, len(rides)+1):
            s, e, v =  rides[i-1]
            non_overlaping_index = bisect_right(ends, s, 0, i-1)
            taken = v + (e-s) + dp[non_overlaping_index]
            not_taken = dp[i-1]
            dp[i] = max(dp[i], max(taken, not_taken))
        return dp[-1]

############################# time exceding
class Solution:
    def maxTaxiEarnings(self, n: int, rides: List[List[int]]) -> int:
        dp = [0 for i in range(n)]
        rides = sorted(rides)
        for ride in rides:
            s,e,tip = ride     
            # why -1 because we are starting dp index positon from 0.
            dp[e-1] = max(dp[e-1], max(dp[e-1-1], e-s+tip+dp[s-1]))
            #.            ^existing val, this is to handle the case where previous points already updated the end location with higher value. 
            #             ex: (1,8,100),(2,6,1),(6,8,2), so here 1,8 updated with highest value but when 6,8 will com, then we will check if the 
            #             end positon is already updated with higher value by other trips or not.
            #                           ^prev_val(not take, ^ take (prev end positon value (starting postition) + current =  if take then then (end-start)+tip +total money before current start trip
            # update all the value from the end to it right side all the values
            # to optimize it do binary search, search the 1st non zero value from 0: start position 
            for i in range(e, n):
                dp[i] = max(dp[i], dp[e-1])
        print(dp)
        return dp[-1]
