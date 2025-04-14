"""
https://leetcode.com/problems/combination-sum/description/

Given an array of distinct integers candidates and a target integer target, return a list of all unique combinations of candidates where the chosen numbers sum to target. You may return the combinations in any order.

The same number may be chosen from candidates an unlimited number of times. Two combinations are unique if the frequency of at least one of the chosen numbers is different.

The test cases are generated such that the number of unique combinations that sum up to target is less than 150 combinations for the given input.

 

Example 1:

Input: candidates = [2,3,6,7], target = 7
Output: [[2,2,3],[7]]
Explanation:
2 and 3 are candidates, and 2 + 2 + 3 = 7. Note that 2 can be used multiple times.
7 is a candidate, and 7 = 7.
These are the only two combinations.
Example 2:

Input: candidates = [2,3,5], target = 8
Output: [[2,2,2,2],[2,3,3],[3,5]]
Example 3:

Input: candidates = [2], target = 1
Output: []


Note: can solved in backtracking . solved in subset pattern. to avoid duplicate take index and always take next index >= currrent index.

"""
=======0/1 knap sack =====
class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        dp = defaultdict(list)
        candidates.sort()
        for c in candidates:
            dp[c].append([c])
        print(dp)
        for i in range(target+1):
            for j in candidates:
                if j <= i:
                    for elem in dp[i-j]:
                        print("for "+str(i)+"--"+ str(elem))
                        if elem == None:
                            continue
                        if elem[-1]> j:
                            continue
                        val = copy.deepcopy(elem)
                        val.append(j)
                        dp[i].append(val)
                        print("for "+str(i)+"--"+ str(dp[i]), str(val))
        print(dp)
        return dp[target]



        



======back tracking =====
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
