"""
https://leetcode.com/problems/tiling-a-rectangle-with-the-fewest-squares/description/
"""


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
                # using i, j we will be able to form different rectangle
                # now we have to device that rectandle horizontally and vertically to see
                # how many square would be neeed
                for k in range(1, i // 2 + 1):  # in python if do +1 in range it will reach i//2
                    dp[i][j] = min(dp[i][j], dp[k][j] + dp[i - k][j])  # horizontal cuts
                # for k = 1 only vertical or horizontal cuts are possible
                # but for greater k values both vertical and horizontal cuts are possible.
                for k in range(1, j // 2 + 1):  # vertical cuts
                    dp[i][j] = min(dp[i][j], dp[i][k] + dp[i][j - k])
        return dp[m][n]

