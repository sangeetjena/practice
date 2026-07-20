```
https://leetcode.com/problems/paint-fence/description/?envType=problem-list-v2&envId=dynamic-programming

You are painting a fence of n posts with k different colors. You must paint the posts following these rules:

Every post must be painted exactly one color.
There cannot be three or more consecutive posts with the same color.
Given the two integers n and k, return the number of ways you can paint the fence.

Input: n = 3, k = 2
Output: 6
Explanation: All the possibilities are shown.
Note that painting all the posts red or all the posts green is invalid because there cannot be three posts in a row with the same color.
Example 2:

Input: n = 1, k = 1
Output: 1
Example 3:

Input: n = 7, k = 2
Output: 42

```
<img width="1486" height="1052" alt="image" src="https://github.com/user-attachments/assets/868707f8-c8b7-4bea-912e-f5e30cdaa443" />


``` py
from collections import defaultdict
class Solution:         
    def numWays(self, n: int, k: int) -> int:
        prev = k
        diff = k
        total = k
        for i in range(1,n):
            prev = diff
            diff = total * (k-1)
            total = prev + diff
        return total



```
