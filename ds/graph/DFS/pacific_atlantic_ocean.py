"""
https://leetcode.com/problems/pacific-atlantic-water-flow/description/

Note: insteed of traversing all nodes just capture left right top and bottom rows touching oceans and run dfs for those cells only
"""


class Solution:
    def runDFS(self, edges, heights, output, ocean):
        # normal dfs template
        dfs = []
        visited = []
        for i,j in edges:
            if (i,j) in visited:
                continue
            dfs.append((i,j))
            while len(dfs)>0:
                x,y = dfs[-1]
                if dfs[-1] in visited:
                    del dfs[-1]
                    continue
                if x>0 and heights[x-1][y] >= heights[x][y]:
                    dfs.append((x-1,y))
                if x< len(heights)-1 and heights[x+1][y] >= heights[x][y]:
                    dfs.append((x+1, y))
                if y>0 and heights[x][y-1] >= heights[x][y]:
                    dfs.append((x,y-1))
                if y< len(heights[0])-1 and heights[x][y+1] >= heights[x][y]:
                    dfs.append((x,y+1))
                output[(x,y)].append(ocean)
                visited.append((x,y))

    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        output = defaultdict(list)
        pacific = []
        atlantic = []
        # capture all points touching ocean. top row, bottom row, left and right 
        for i in range(len(heights[0])):
            pacific.append((0,i))
            atlantic.append((len(heights)-1,i))
        # capture all points touching ocean. top row, bottom row, left and right 
        for i in range(len(heights)):
            pacific.append((i,0))
            atlantic.append((i,len(heights[0])-1))
        # run dfs for atlantic and pacific once 
        # and capture common cell from pacific and atlantic
        self.runDFS(pacific,heights, output, "p")
        self.runDFS(atlantic,heights, output, "a")
        print([[key[0],key[1]] for key in output.keys() if len(output[key])==2])
        return [[key[0],key[1]] for key in output.keys() if len(output[key])==2]

        

                
        
