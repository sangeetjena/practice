"""
he n-queens puzzle is the problem of placing n queens on an n x n chessboard such that no two queens attack each other.

Given an integer n, return all distinct solutions to the n-queens puzzle. You may return the answer in any order.

Each solution contains a distinct board configuration of the n-queens' placement, where 'Q' and '.' both indicate a queen and an empty space, respectively.

 

Example 1:


Input: n = 4
Output: [[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]
Explanation: There exist two distinct solutions to the 4-queens puzzle as shown above


"""

class Solution:
    def solveNQueens(self, n: int) -> List[List[str]]:
        res = []
        board = [["." for _ in range(n)] for _ in range(n)]

        def backtrack(row):
            if row == n:
                res.append(["".join(r) for r in board])
                return
            for col in range(n):
                if isSafe(row, col):
                    board[row][col] = 'Q'
                    backtrack(row + 1)
                    # if return to the original positoin i,j then the position can't be taken, hene reset it.
                    board[row][col] = '.'

        def isSafe(row, col):
            # check diagonally, x-axis ans y-axis value.
            for i in range(row):
                if board[i][col] == 'Q':
                    return False
            for i in range(1, min(row, col) + 1):
                if board[row - i][col - i] == 'Q':
                    return False
            for i in range(1, min(row, n - 1 - col) + 1):
                if board[row - i][col + i] == 'Q':
                    return False
            return True

        backtrack(0)
        return res
