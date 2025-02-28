"""
https://leetcode.com/problems/paint-house/description/?envType=problem-list-v2&envId=dynamic-programming

There is a row of n houses, where each house can be painted one of three colors: red, blue, or green. The cost of painting each house with a certain color is different. You have to paint all the houses such that no two adjacent houses have the same color.

The cost of painting each house with a certain color is represented by an n x 3 cost matrix costs.

For example, costs[0][0] is the cost of painting house 0 with the color red; costs[1][2] is the cost of painting house 1 with color green, and so on...
Return the minimum cost to paint all houses.

 

Example 1:

Input: costs = [[17,2,17],[16,16,5],[14,3,19]]
Output: 10
Explanation: Paint house 0 into blue, paint house 1 into green, paint house 2 into blue.
Minimum cost: 2 + 5 + 3 = 10.



"""

class Solution:
    def minCost(self, costs: List[List[int]]) -> int:
        # this problem is similar to arrange cake in the shop problem
        # i just need the previous set price to decide the next minimum cost 
        for i in range(1,len(costs)):
            for j in range(len(costs[0])):
                costs[i][j] += min([costs[i-1][k] for k in range(len(costs[0])) if k != j])
        return min(costs[-1])
        
