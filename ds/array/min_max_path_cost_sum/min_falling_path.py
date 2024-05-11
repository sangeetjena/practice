"""
https://leetcode.com/problems/minimum-falling-path-sum/description/
"""


class Solution:
    def minFallingPathSum(self, matrix: List[List[int]]) -> int:
        dp = matrix[0] + [99999]
        for i in range(1, len(matrix[0])):
            for j in range(len(matrix[0])):
                if (j == 0):
                    matrix[i][j] = matrix[i][j] + min(dp[j], dp[j + 1])
                else:
                    matrix[i][j] = matrix[i][j] + min(dp[j - 1], dp[j], dp[j + 1])
            dp = matrix[i] + [99999]
        return min(matrix[-1])
