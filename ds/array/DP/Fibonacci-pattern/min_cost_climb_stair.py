"""
https://leetcode.com/problems/min-cost-climbing-stairs/submissions/1377185827/

Note: similar to climb stair but add cost and add one extra index to represt top floor.
"""
class Solution:
    def minCostClimbingStairs(self, cost: List[int]) -> int:
        cost+=[0]
        for i in range(2,len(cost)):
            cost[i] = cost[i] + min(cost[i-1], cost[i-2])
        return cost[-1]
