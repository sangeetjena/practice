"""
https://leetcode.com/problems/minimum-cost-to-cut-a-stick/description/

Note: this has to try with all possible cuts and take the min from them
Option1:-(top down approach) ( mamoisation) 1st take one cut and check what is it s left and right size and cost.
then compare with other cuts and take the min form that cut.
"""
class Solution:
    
    def minCost(self, n: int, cuts: List[int]) -> int:
        dp = {}
        def dfs(l,r):
            if l-r==1:
                return 0
            if (l,r) in dp.keys():
                return dp[(l,r)]
            res = float("inf")
            for cut in cuts:

                if l<cut<r:
                    res = min(res, (r-l) + dfs(l,cut) + dfs(cut,r))
            dp[(l,r)] = 0 if res == float("inf") else res
            return dp[(l,r)]
        return dfs(0,n)
