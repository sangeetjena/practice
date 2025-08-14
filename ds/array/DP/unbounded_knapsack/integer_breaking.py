"""
https://leetcode.com/problems/integer-break/description/

Given an integer n, break it into the sum of k positive integers, where k >= 2, and maximize the product of those integers.

Return the maximum product you can get.

 

Example 1:

Input: n = 2
Output: 1
Explanation: 2 = 1 + 1, 1 × 1 = 1.
Example 2:

Input: n = 10
Output: 36
Explanation: 10 = 3 + 3 + 4, 3 × 3 × 4 = 36.

"""
class Solution:
    def integerBreak(self, n: int) -> int:
        dp = [1 for i in range(n+1)]
        for i in range(2,len(dp)):
            for j in range(1,i):
              # why 2nd max: because we need to check if we will take the remaining (substreaciton from main value) value as a whole  (i-j)
              # or if we will break the remaining value (i.e multiplication of the values, if the remaining value will be broken further) dp[i-j].
              # which one will be bigger that we have to take to maximize the value.
              # ex: for 4 - we can brak it to 2+2 = 2*2 = 4 but if weill break it further -> 2+ (1+1) then multiplication will be 2 only 
              # but if we would have taken 2 as a whole then multiplication value would have been more.
                dp[i] = max(dp[i], j*max(dp[i-j], i-j))
                print(i,j,dp[i-j])
        print(dp)
        return dp[-1]
