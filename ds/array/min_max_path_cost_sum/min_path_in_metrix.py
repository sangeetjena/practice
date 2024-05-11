"""
https://leetcode.com/problems/minimum-path-sum/description/
"""
class Solution:
    def minPathSum(self, grid: List[List[int]]) -> int:
        dummyarr = [[9999 for i in range(len(grid[0]))]]
        grid = dummyarr + grid
        for i in range(len(grid)):
            grid[i] = [9999]+grid[i]
        for i in range(1,len(grid)):
            for j in range(1,len(grid[0])):
                if j == 1 and i ==1:
                    continue
                grid[i][j] = min(grid[i-1][j], grid[i][j-1])+grid[i][j]
        return grid[-1][-1]