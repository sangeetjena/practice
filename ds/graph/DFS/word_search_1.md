```
https://leetcode.com/problems/word-search/description/


Given an m x n grid of characters board and a string word, return true if word exists in the grid.

The word can be constructed from letters of sequentially adjacent cells, where adjacent cells are
horizontally or vertically neighboring. The same letter cell may not be used more than once.


Note: simple dfs proble but when found visited remove element form visited list and remove from the dfs.
```
<img width="684" height="743" alt="image" src="https://github.com/user-attachments/assets/12da1578-7764-48d5-b65a-39f93e273811" />
<img width="684" height="357" alt="image" src="https://github.com/user-attachments/assets/9f375bd1-4679-48ca-add3-8adfbfeb8af3" />



``` python
class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        dfs = []
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == word[0]:
                    dfs = [[i,j]]
                    visited = set()
                    newword = ""
                    while dfs:
                        x,y = dfs[-1]
                        # check if the char is alrady visited then remove from dfs list and remove from visited to allow other combination to take this character.
                        if (x,y) in visited:
                            del dfs[-1]
                            newword = newword[:len(newword)-1]
                            if (x,y) in visited:
                                visited.remove((x,y))
                            continue
                        newword+=board[x][y]
                        # check new match the desired word then return 
                        if newword == word:
                            return True
                        #check if the next charrector is matching the next charector in the word, then only add to dfs.
                        if x>=0 and x<len(board)-1 and ((x+1,y) not in visited and  board[x+1][y] == word[len(newword)]):
                            dfs.append([x+1,y])
                        if x<=len(board) and x>0 and ( (x-1,y) not in visited and  board[x-1][y] == word[len(newword)]):
                            dfs.append([x-1,y])
                        if y>=0 and y<len(board[0])-1 and ( (x,y+1) not in visited and  board[x][y+1] == word[len(newword)]):
                            dfs.append([x,y+1])
                        if y<=len(board[0]) and y>0 and ( (x,y-1) not in visited and  board[x][y-1] == word[len(newword)]):
                            dfs.append([x,y-1])
                        visited.add((x,y))
        return False

                        

        

```
