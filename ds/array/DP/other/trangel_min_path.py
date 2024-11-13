"""
https://leetcode.com/problems/triangle/?envType=problem-list-v2&envId=dynamic-programming

Given a triangle array, return the minimum path sum from top to bottom.

For each step, you may move to an adjacent number of the row below. More formally, if you are on index i on the current row, you may move to either index i or index i + 1 on the next row.

 

Example 1:

Input: triangle = [[2],[3,4],[6,5,7],[4,1,8,3]]
Output: 11
Explanation: The triangle looks like:
   2
  3 4
 6 5 7
4 1 8 3
The minimum path sum from top to bottom is 2 + 3 + 5 + 1 = 11 (underlined above).


Note: similar to arrange cake by colour problem, this also can be solved using dfs and bfs like a tree. i have given all 3 solutions.

"""
===========DP===========
class Solution:
    def minimumTotal(self, triangle: List[List[int]]) -> int:
        #similar to colur cake problem 
        for i in range(1,len(triangle)):
            for j in range(len(triangle[i])):
                if j==0:
                    triangle[i][j] = triangle[i][j] + (triangle[i-1][j])
                elif j == len(triangle[i])-1:
                    triangle[i][j] = triangle[i][j] + (triangle[i-1][j-1])
                else:
                    # add min between it previous parents to the current value
                    triangle[i][j] = triangle[i][j] + min(triangle[i-1][j-1],triangle[i-1][j] )
        print(triangle)
        # min will be available in the last row.
        return min(triangle[-1])

            



==========BFS==========
class Solution:
    def minimumTotal(self, triangle: List[List[int]]) -> int:
        i = 0
        bfs = []
        visited = set()
        bfs.append((0,0,triangle[0][0]))
        minval = float("inf")
        while bfs:
            i,j,w = bfs[-1]
            del bfs[-1]
            # currval+=w
            # print(dfs)
            if j>=len(triangle)-1:
                minval = min(w, minval)
                # print("minval" + str(minval))
                continue
            bfs.append((i,j+1,triangle[j+1][i]+w))
            bfs.append((i+1,j+1,triangle[j+1][i+1]+w))
        return minval
            

==========DFS===========
class Solution:
    def minimumTotal(self, triangle: List[List[int]]) -> int:
        i = 0
        dfs = []
        visited = set()
        dfs.append((0,0,triangle[0][0]))
        minval = float("inf")
        while dfs:
            i,j,w = dfs[-1]
            # currval+=w
            # print(dfs)
            if j>=len(triangle)-1:
                minval = min(w, minval)
                # print("minval" + str(minval))
                del dfs[-1]
                continue
            if (i,j) in visited:
                del dfs[-1]
                visited.remove((i,j))
                continue
            dfs.append((i,j+1,triangle[j+1][i]+w))
            dfs.append((i+1,j+1,triangle[j+1][i+1]+w))
            visited.add((i,j))
        return minval
            
