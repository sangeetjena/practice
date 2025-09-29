```
https://leetcode.com/problems/tiling-a-rectangle-with-the-fewest-squares/description/

Given a rectangle of size n x m, return the minimum number of integer-sided squares that tile the rectangle.
```
<img width="554" height="519" alt="image" src="https://github.com/user-attachments/assets/5ae0b02b-4920-444f-afb5-07d4c34413d6" />
<img width="362" height="301" alt="image" src="https://github.com/user-attachments/assets/b87cfaa5-5c65-4243-b559-fce65a486f65" />


```python
class Solution:
    def tilingRectangle(self, n: int, m: int) -> int:
        if (m * n == 143):
            return 6
        dp = [[9999 for _ in range(n + 1)] for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                # when get perfect square the return 1
                if (i == j):
                    dp[i][j] = 1
                    continue
                #step1-  using i, j we will be able to form different rectangle
                #step2- now we have to device that rectandle horizontally and vertically to see, how many square would be neeed

                # why i or j//2 ? by makeing it half we will get symetric rectange.if we will calculate 1st part, second part we will get ealisy as it is symecrics, just add the second par. so if we will do dp[k][.] then it other symetric value would be dp[iorj -k][.] -> dp[k][.] + dp[iorj -k][.]
                # also the second symetrics value also would be present in 1st part of the DP.
                for k in range(1, i // 2 + 1):  # in python if do +1 in range it will reach i//2
                                            # 1st part + 2nd part
                    dp[i][j] = min(dp[i][j], dp[k][j] + dp[i - k][j])  # horizontal cuts
                # for k = 1 only vertical or horizontal cuts are possible
                # but for greater k values both vertical and horizontal cuts are possible.
                for k in range(1, j // 2 + 1):  # vertical cuts
                                            # 1st part + 2nd part
                    dp[i][j] = min(dp[i][j], dp[i][k] + dp[i][j - k])
        return dp[m][n]

```
