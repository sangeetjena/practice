"""74. Search a 2D Matrix
Medium
12.4K
350
company
Amazon
company
Apple
company
Bloomberg
You are given an m x n integer matrix matrix with the following two properties:

Each row is sorted in non-decreasing order.
The first integer of each row is greater than the last integer of the previous row.
Given an integer target, return true if target is in matrix or false otherwise.

You must write a solution in O(log(m * n)) time complexity.



Example 1:


Input: matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3
Output: true"""
from typing import List
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        for lst in matrix:
            if lst[0] <= target <= lst[-1]:
                for i in lst:
                    if i == target:
                        print("found")
                        return
        print("not found")

matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]]
obj = Solution()
obj.searchMatrix(matrix, 3)