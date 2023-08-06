"""
Given an m x n board of characters and a list of strings words, return all words on the board.

Each word must be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once in a word.

Example 1:
Input: board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]], words = ["oath","pea","eat","rain"]
Output: ["eat","oath"]
"""
import copy
class Solution:
    def bst(self, metrix, word, startingPostion):
        stack = []
        visited = []
        newposition  =copy.deepcopy(startingPostion)
        stack.append(word[0])
        del word[0]
        for letter in word:
            x = newposition[0]
            x1 = newposition[0] - 1
            y = newposition[1]
            y1 = newposition[1] - 1

            if metrix[x+1][y] == letter:


    def searchWord(self, metrix, words):
        for word in words:
                startingLetter = word[0]
                searchStartingIndex = (0,0)
                for i in range(len(metrix)):
                    foundornot = 0
                    for y in range(len(metrix[i])):
                        if startingLetter == metrix[y]:
                            searchStartingIndex = (i, y)
                            foundornot = self.bst(metrix,word, searchStartingIndex)
                            if foundornot == 1:
                                break
                    if foundornot ==1:
                        break
