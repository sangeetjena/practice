"""
https://leetcode.com/problems/paint-house/description/
ind= 0, 1, 2
  [[17,2,17],
   [16,16,5],
   [14,3,19]]

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
