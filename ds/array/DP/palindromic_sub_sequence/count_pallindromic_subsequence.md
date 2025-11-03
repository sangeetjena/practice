```
https://leetcode.com/problems/count-different-palindromic-subsequences/description/

Given a string s, return the number of different non-empty palindromic subsequences in s. Since the answer may be very large, return it modulo 109 + 7.

A subsequence of a string is obtained by deleting zero or more characters from the string.

A sequence is palindromic if it is equal to the sequence reversed.

Two sequences a1, a2, ... and b1, b2, ... are different if there is some i for which ai != bi.

 

Example 1:

Input: s = "bccb"
Output: 6
Explanation: The 6 different non-empty palindromic subsequences are 'b', 'c', 'bb', 'cc', 'bcb', 'bccb'.
Note that 'bcb' is counted only once, even though it occurs twice.
Example 2:

Input: s = "abcdabcdabcdabcdabcdabcdabcdabcddcbadcbadcbadcbadcbadcbadcbadcba"
Output: 104860361
Explanation: There are 3104860382 different non-empty palindromic subsequences, which is 104860361 modulo 109 + 7.

https://www.youtube.com/watch?v=NdpolO4sM3k

```

``` python
class Solution:
    def countPalindromicSubsequences(self, s: str) -> int:
        n = len(s)
        mod = 10**9 + 7
        dp = [[0] * n for _ in range(n)]

        for i in range(n):
            dp[i][i] = 1  # single letters

        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                if s[i] == s[j]:
                    low, high = i + 1, j - 1
                    while low <= high and s[low] != s[i]:
                        low += 1
                    while low <= high and s[high] != s[j]:
                        high -= 1

                    if low > high:  # no same character inside
                        dp[i][j] = dp[i + 1][j - 1] * 2 + 2
                    elif low == high:  # one same character inside
                        dp[i][j] = dp[i + 1][j - 1] * 2 + 1
                    else:  # more than one same character inside
                        dp[i][j] = dp[i + 1][j - 1] * 2 - dp[low + 1][high - 1]
                else:
                    dp[i][j] = dp[i + 1][j] + dp[i][j - 1] - dp[i + 1][j - 1]

                dp[i][j] = (dp[i][j] + mod) % mod

        return dp[0][n - 1]


```
