"""
https://leetcode.com/problems/combination-sum/description/
Note: can solved in backtracking . solved in subset pattern.

"""

class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        total_list = []
        templist = []
        def total_sums(candidates, target, templst,i):
            print(type(templst))
            print(templst)
            if target==0:
                total_list.append(templst)
                return
            if target < 0:
                return
            for i in range(i, len(candidates)):
                total_sums(candidates, target-candidates[i],templst+[candidates[i]], i)
        total_sums(candidates, target, templist,0)
        return total_list
