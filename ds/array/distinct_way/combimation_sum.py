"""
https://leetcode.com/problems/combination-sum-iv/

Given an array of distinct integers nums and a target integer target, return the number of possible combinations that add up to target.

The test cases are generated so that the answer can fit in a 32-bit integer.

 

Example 1:

Input: nums = [1,2,3], target = 4
Output: 7
Explanation:
The possible combination ways are:
(1, 1, 1, 1)
(1, 1, 2)
(1, 2, 1)
(1, 3)
(2, 1, 1)
(2, 2)
(3, 1)
Note that different sequences are counted as different combinations.

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
                    
                
        
