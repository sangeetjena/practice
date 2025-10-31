```
https://leetcode.com/problems/interleaving-string/description/
https://www.youtube.com/results?search_query=97.+Interleaving+String

Given strings s1, s2, and s3, find whether s3 is formed by an interleaving of s1 and s2.

An interleaving of two strings s and t is a configuration where s and t are divided into n and m substrings respectively, such that:

s = s1 + s2 + ... + sn
t = t1 + t2 + ... + tm
|n - m| <= 1
The interleaving is s1 + t1 + s2 + t2 + s3 + t3 + ... or t1 + s1 + t2 + s2 + t3 + s3 + ...
Note: a + b is the concatenation of strings a and b.
```

<img width="732" height="635" alt="image" src="https://github.com/user-attachments/assets/32e7ca40-9686-4b66-87fe-c48ea0920f4a" />

``` python
class Solution:
    def isInterleave(self, s1: str, s2: str, s3: str) -> bool:
        m, n = len(s1), len(s2)
        if m + n != len(s3):
            return False
        dp = [[False] * (n + 1) for _ in range(m + 1)]
        # base case :if not element selected then set that index to true.
        dp[0][0] = True
        # base case: its previous index value should be true and the current char should match with s3 same index
        for i in range(1, m + 1):
            dp[i][0] = dp[i - 1][0] and s1[i - 1] == s3[i - 1]
        for j in range(1, n + 1):
            dp[0][j] = dp[0][j - 1] and s2[j - 1] == s3[j - 1]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                choose_s1, choose_s2 = False, False
                if s1[i - 1] == s3[i + j - 1]:
                    choose_s1 = dp[i - 1][j]
                if s2[j - 1] == s3[i + j - 1]:
                    choose_s2 = dp[i][j - 1]
                dp[i][j] = choose_s1 or choose_s2

        return dp[m][n]
```
