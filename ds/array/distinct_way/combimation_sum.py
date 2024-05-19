"""
https://leetcode.com/problems/combination-sum-iv/

"""
class Solution:
    def combinationSum4(self, nums: List[int], target: int) -> int:
        # similar to the 0/1 nap sack problem.
        dp = [0 for _ in range(target+1)]
        dp[0] = 1
        for i in range(target+1):
            for j in nums:
                if j <= i:
                    dp[i] = dp[i] +  dp[i-j]
        print(dp)
        return dp[target]
                    
                
        
