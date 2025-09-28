```
https://leetcode.com/problems/minimum-falling-path-sum/description/

Given an n x n array of integers matrix, return the minimum sum of any falling path through matrix.

A falling path starts at any element in the first row and chooses the element in the next row that is either directly below or diagonally left/right. Specifically, the next element from position (row, col) will be (row + 1, col - 1), (row + 1, col), or (row + 1, col + 1).

Note:

```
<img width="628" height="629" alt="image" src="https://github.com/user-attachments/assets/7c96e06d-86c0-4012-93cb-80e753d896f6" />
<img width="525" height="485" alt="image" src="https://github.com/user-attachments/assets/efb7f711-803d-45c3-98af-245088e86d09" />



``` python


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

```
