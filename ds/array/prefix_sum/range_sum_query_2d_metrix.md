
```
https://leetcode.com/problems/range-sum-query-2d-immutable/description/


Given a 2D matrix matrix, handle multiple queries of the following type:

Calculate the sum of the elements of matrix inside the rectangle defined by its upper left corner (row1, col1) and lower right corner (row2, col2).
Implement the NumMatrix class:

NumMatrix(int[][] matrix) Initializes the object with the integer matrix matrix.
int sumRegion(int row1, int col1, int row2, int col2) Returns the sum of the elements of matrix inside the rectangle defined by its upper left corner (row1, col1) and lower right corner (row2, col2).
You must design an algorithm where sumRegion works on O(1) time complexity.



Input
["NumMatrix", "sumRegion", "sumRegion", "sumRegion"]
[[[[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]]], [2, 1, 4, 3], [1, 1, 2, 2], [1, 2, 2, 4]]
Output
[null, 8, 11, 12]

Explanation
NumMatrix numMatrix = new NumMatrix([[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]]);
numMatrix.sumRegion(2, 1, 4, 3); // return 8 (i.e sum of the red rectangle)
numMatrix.sumRegion(1, 1, 2, 2); // return 11 (i.e sum of the green rectangle)
numMatrix.sumRegion(1, 2, 2, 4); // return 12 (i.e sum of the blue rectangle)

Note: This is same as prefix sum problem , but in 2d metrix we are captureing sum of entire grid at the end of the grid cornor location.
so to get total sum of grid  = sum of current row + sum of previous grid (value stored at above row, same colum)

 ```

Example 1:
<img width="446" height="456" alt="image" src="https://github.com/user-attachments/assets/0f2ff003-85d4-482e-b2ec-92191a666467" />


``` python
class NumMatrix:
    def __init__(self, matrix: list[list[int]]):
        n = len(matrix)
        m = len(matrix[0]) if n else 0
        self.ps = [[0]*(m+1) for _ in range(n+1)]
        # total sum of a squre is stored at the end cornor location of the grid.
        for i in range(1,len(self.ps)):
            total = 0
            for j in range(1, len(self.ps[0])):
                # total is prefix sum of the current row
                total += matrix[i-1][j-1]
                # total squre sum = total prefix sum + total sum of previous square.
                self.ps[i][j] = total + self.ps[i-1][j]

    def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
        ps = self.ps
        # increment row and column value as we have added one extra row and columns in the ps metrics
        row1+=1
        row2+=1
        col1+=1
        col2+=1
        return ps[row2][col2] - ps[row1-1][col2] - ps[row2][col1-1] + ps[row1-1][col1-1]
```
<img width="616" height="612" alt="image" src="https://github.com/user-attachments/assets/94f2cfb0-a1a1-4a25-ab76-b8252ba59f04" />
