```
https://leetcode.com/problems/valid-sudoku/description/

Determine if a 9 x 9 Sudoku board is valid. Only the filled cells need to be validated according to the following rules:

Each row must contain the digits 1-9 without repetition.
Each column must contain the digits 1-9 without repetition.
Each of the nine 3 x 3 sub-boxes of the grid must contain the digits 1-9 without repetition.
Note:

A Sudoku board (partially filled) could be valid but is not necessarily solvable.
Only the filled cells need to be validated according to the mentioned rules.


Note: for bigger metrics just search for left and right ( use hash map and bit masking)
for inner small box use hash map and check if any number repeated or not (all shell in side the smaller box give same index postion.
```
<img width="288" height="273" alt="image" src="https://github.com/user-attachments/assets/a7005ab6-171b-42e6-839b-994cf2cd96a7" />

``` python
class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        mask = {}
        for i in range(len(board)):
            for j in range(len(board)):
                # check horizontally if the element is duplicate
                if board[i][j] == '.':
                    continue
                if 'x'+str(i) in mask.keys():
                    if (mask['x'+str(i)] & (1<<int(board[i][j]))) > 0:
                        return False
                    else:
                        mask['x'+str(i)] = (1<<int(board[i][j])) | mask['x'+str(i)]
                else:
                    mask['x'+str(i)] = 1<<int(board[i][j]) 
                # check vertically
                if 'y'+str(j) in mask.keys():
                    if mask['y'+str(j)] & (1<<int(board[i][j])) > 0:
                        return False
                    else:
                        mask['y'+str(j)] = (1<<int(board[i][j])) | mask['y'+str(j)]
                else:
                    mask['y'+str(j)] = 1<<int(board[i][j])
                # not check inner grid. entire small grid single location and store each number used in bit mask.
                gridnum_x = i//3
                gridnum_y = j//3
                if str(gridnum_x)+str(gridnum_y) in mask:
                    if mask[str(gridnum_x)+str(gridnum_y)] & (1<<int(board[i][j])) > 0:
                        return False
                    else:
                        mask[str(gridnum_x)+str(gridnum_y)] = mask[str(gridnum_x)+str(gridnum_y)] | (1<<int(board[i][j]))
                else:
                    mask[str(gridnum_x)+str(gridnum_y)] = (1<<int(board[i][j]))
        
        return True



```
