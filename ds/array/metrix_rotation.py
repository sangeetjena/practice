class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.
        """
        for i in range(0, len(matrix[0])):
            for j in range(i, len(matrix)):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        for i in range(0, len(matrix)):
            e = len(matrix[i])-1
            s = 0
            while e > s:
                matrix[i][s], matrix[i][e] = matrix[i][e], matrix[i][s]
                s +=1
                e -=1
