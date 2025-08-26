"""
https://leetcode.com/problems/minimum-path-sum/description/

Given a m x n grid filled with non-negative numbers, find a path from top left to bottom right, which minimizes the sum of all numbers along its path.

Note: You can only move either down or right at any point in time.

Example 1:


Input: grid = [[1,3,1],[1,5,1],[4,2,1]]
Output: 7
Explanation: Because the path 1 → 3 → 1 → 1 → 1 minimizes the sum.
Example 2:

Input: grid = [[1,2,3],[4,5,6]]
Output: 12

 Note: take minimum between above row same position and current row previous positon and add it to the current row.
 i.e: grid[i][j] + min(grid[i][j-1],  grid[i-1][j])

"""

class Solution:
    def minPathSum(self, grid: List[List[int]]) -> int:
        for i in range(len(grid)):
            for j in range(len(grid[0])):

                if i ==0 and j == 0 :
                    pass
                elif j == 0:
                    grid[i][j] = grid[i-1][j] + grid[i][j]
                elif i==0:
                    grid[i][j] = grid[i][j-1] + grid[i][j]
                else:
                    grid[i][j] = grid[i][j] + min(grid[i][j-1],  grid[i-1][j])
        print(grid)
        return grid[-1][-1]
