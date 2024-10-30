"""
https://leetcode.com/problems/word-search-ii/description/
Given an m x n grid of characters board and a string word, return true if word exists in the grid.

The word can be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once.

 

Example 1:


Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
Output: true

Note: simple dfs , but while back tracking remove node from visited set

"""

class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        dfs = []
        for p in range(len(board)):
            for q in range(len(board[0])):
                # if 1st char match then start the dfs search else no need of search
                if board[p][q]== word[0]:
                    dfs=[(p,q,0)]
                    visited = set()
                    # start the search
                    while dfs:
                        x,y,i = dfs[-1]
                        # if char not match or char position already visited then delete and decrement i.
                        if (x,y) in visited:
                            # removing from visited sothat if this node will come from some other branch (parent) can continue.
                            visited.remove((x,y))
                            del dfs[-1]
                            continue
                        # if all char found ,i.e i==len(word)-1 then return true
                        if i==len(word)-1 and board[x][y]==word[i]:
                            return True
                        # find all 4 position in the board
                        if x< len(board)-1 and (x+1, y) not in visited and board[x+1][y]==word[i+1]:
                            dfs.append((x+1,y,i+1))
                        if x>0 and (x-1, y) not in visited and board[x-1][y]==word[i+1]:
                            dfs.append((x-1,y,i+1))
                        if y< len(board[0])-1 and (x, y+1) not in visited and board[x][y+1]==word[i+1]:
                            dfs.append((x,y+1,i+1))
                        if y> 0 and (x, y-1) not in visited and board[x][y-1]==word[i+1]:
                            dfs.append((x,y-1,i+1))
                        visited.add((x,y))
        return False


       

