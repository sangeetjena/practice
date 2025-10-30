"""
https://leetcode.com/problems/paint-house/description/
ind= 0, 1, 2
  [[17,2,17],
   [16,16,5],
   [14,3,19]]

There is a row of n houses, where each house can be painted one of three colors: red, blue, or green. The cost of painting each house with a certain color is different. 
You have to paint all the houses such that no two adjacent houses have the same color.
The cost of painting each house with a certain color is represented by an n x 3 cost matrix costs.

For example, costs[0][0] is the cost of painting house 0 with the color red; costs[1][2] is the cost of painting house 1 with color green, and so on...
Return the minimum cost to paint all houses.

Example 1:

Input: costs = [[17,2,17],[16,16,5],[14,3,19]]
Output: 10
Explanation: Paint house 0 into blue, paint house 1 into green, paint house 2 into blue.
Minimum cost: 2 + 5 + 3 = 10.
Example 2:

Input: costs = [[7,6,2]]
Output: 2

Note: same colour reprented the same index position in the grid, so when calculating min colour for a house take current colour and select min colour of its previous house except 
current index position value (represent same colour).

similar problem: arrange cakes colour in shop

"""
import copy
class Solution:
    def minCost(self, costs: List[List[int]]) -> int:
        for i in range(1,len(costs)):
            for j in range(len(costs[0])):
                # check always its previous house all the index except same index (as same index represent same colour) and find the min.
                mn = min([costs[i-1][x] for x in range(len(costs[0])) if x !=j])
                # add the min cost of previous house and add it to the current house cost
                costs[i][j] = costs[i][j]+ mn
        return min(costs[-1])
