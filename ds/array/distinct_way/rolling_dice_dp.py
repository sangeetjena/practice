"""
https://leetcode.com/problems/number-of-dice-rolls-with-target-sum/
https://www.youtube.com/watch?v=hfUxjdjVQN4&t=1s

You have n dice, and each dice has k faces numbered from 1 to k.

Given three integers n, k, and target, return the number of possible ways (out of the kn total ways) to roll the dice, so the sum of the face-up numbers equals target. Since the answer may be too large, return it modulo 109 + 7.

 

Example 1:

Input: n = 1, k = 6, target = 3
Output: 1
Explanation: You throw one die with 6 faces.
There is only one way to get a sum of 3.
"""
class Solution:
    def numRollsToTarget(self, n: int, k: int, target: int) -> int:
        mod = 10**9+7
        dp = [0 for _ in range(target+1)]
        dp[0] = 1
        for dice in range(1, n+1):
            next_dp  = [0 for _ in range(target+1)]
            for val in range(1, k+1):
                for tgt in range(val, target+1):
                    next_dp[tgt] = (next_dp[tgt] + dp[tgt-val])%mod
            dp = next_dp
        return dp[target]
