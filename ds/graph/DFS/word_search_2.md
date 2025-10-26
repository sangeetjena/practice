```
https://leetcode.com/problems/word-search-ii/description/
Given an m x n grid of characters board and a string word, return true if word exists in the grid.

The word can be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or
vertically neighboring. The same letter cell may not be used more than once.

 

Example 1:


Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
Output: true

Note: simple dfs , but while back tracking remove node from visited set

```
<img width="888" height="718" alt="image" src="https://github.com/user-attachments/assets/db62186c-9f8e-4de1-aa6b-f754f8c0ae2f" />

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

    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        result = []
        for word in words:
            if self.exist(board, word):
                result.append(word)
        return result

```


``` python

class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        total_words = []
        # take one word at a time
        for word in words:
            #search 1st word in the grid and start dfs search
            for i in range(len(board)):
                for j in range(len(board[0])):
                    if word[0] == board[i][j]:
                        dfs = [(i,j)]
                        curr_word = []
                        visited = set()
                        while dfs:
                            x,y = dfs[-1]
                            curr_word.append(board[x][y])
                            print("".join(curr_word),word[:len(curr_word)] )
                            # if the char we have taken will not contribute to form the word or if char is already visited then
                            # remove it from the visited list and from the dfs
                            if "".join(curr_word) != word[:len(curr_word)] or (x,y) in visited:
                                del dfs[-1]
                                if (x,y) in visited:
                                    visited.remove((x,y))
                                del curr_word[-1]
                                continue
                            if "".join(curr_word) == word:
                                if word not in total_words:
                                    total_words.append("".join(curr_word))
                            # find all letters at its surrounding and add it to the dfs
                            if x == 0 and len(board)-1>0:
                                dfs.append((x+1,y))
                            if x == len(board)-1 and len(board)-1>0:
                                dfs.append((x-1,y))
                            if x >0 and x< len(board)-1:
                                dfs.append((x-1,y))
                                dfs.append((x+1,y))

                            if y == 0 and len(board[0])-1>0:
                                dfs.append((x,y+1))
                            if y == len(board[0])-1 and len(board[0])-1>0:
                                dfs.append((x,y-1))
                            if y >0 and y< len(board[0])-1:
                                dfs.append((x,y-1))
                                dfs.append((x,y +1))

                            visited.add((x,y))
        return total_words

```

