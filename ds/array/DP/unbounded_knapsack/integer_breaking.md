```
343. Integer Break
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


```

```python
class Solution:
    def integerBreak(self, n: int) -> int:
        dp = [1 for i in range(n+1)]
        for i in range(2,len(dp)):
            for j in range(1,i):
                # take all element and check for which combination we are getting the max values.
                # when we are getting max value of i-j, we need to check what is the highest value we 
                # will gett by taking all combinatin to for dp[i-j] value vs taking i-j as a whole.
                # to form 2 => 1+1 and product is 1 vs if we will take 2 as a whole we will get larger value to form subsequent products.
                dp[i] = max(dp[i], j*max(dp[i-j], i-j))
                print(i,j,dp[i-j])
        print(dp)
        return dp[-1]

```
