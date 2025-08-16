```
279. Perfect Squares

Given an integer n, return the least number of perfect square numbers that sum to n.

A perfect square is an integer that is the square of an integer; in other words,
it is the product of some integer with itself. For example, 1, 4, 9, and 16 are perfect squares while 3 and 11 are not.

 

Example 1:

Input: n = 12
Output: 3
Explanation: 12 = 4 + 4 + 4.
Example 2:

Input: n = 13
Output: 2
Explanation: 13 = 4 + 9.


Note: this simular to the integer breaking problem
only difference is take numbers which is perfect square.
```
```python
#Solutions
import math
class Solution:
    def numSquares(self, n: int) -> int:
        dp = [9999 for i in range(n+1)]
        pf_square = []
# calculate square root and then multiply it to form the same number. to check if the number is a perfect square or not.
        for i in range(1, n+1):
            root  = int(math.isqrt(i))
            if (root * root) == i:
                pf_square.append(i)
        print(pf_square)
        for i in range(n+1):
            for j in pf_square:
                # this case to form the number it self is a perfect square.
                if j==i:
                    dp[i] = 1
                # after substracting the perfect square value if the remaining value is also prenet in dbt 
                # then check how many perfect square was needed to form that value and add 1 to calculate total perfect square.
                elif j<i and dp[i-j] !=0:
                    dp[i] = min(dp[i], dp[i-j]+1)
        print(dp)
        return dp[-1]


        

```
