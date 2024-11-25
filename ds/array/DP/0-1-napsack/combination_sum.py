"""
https://leetcode.com/problems/combination-sum/description/
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
