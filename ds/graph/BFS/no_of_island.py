"""
https://leetcode.com/problems/number-of-islands/description/

Note: bfs is faster than dfs , as in dfs we need visted array taking more time.

"""
from collections import deque
class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        queue = deque([])
        count = 0
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == '0':
                    continue
                count +=1
                queue.append((i,j))
                while len(queue):
                    p,q = queue.pop()
                    grid[p][q]='0'
                    print(p,q)
                    if p>0 and grid[p-1][q]=='1':
                        queue.append((p-1, q))
                    if p<len(grid)-1 and grid[p+1][q]=='1':
                        queue.append((p+1, q))
                    if q>0 and grid[p][q-1]=='1':
                        queue.append((p, q-1))
                    if q<len(grid[0])-1 and grid[p][q+1]=='1':
                        queue.append((p, q+1))
        return count

        
