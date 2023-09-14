"""
Given the length and width of a grid with obstacles inside it. Calculate how many ways can move from top-left to bottom-right. You can only move either down or right.

Example:
In the input, 1 means obstacle, and 0 means no block.

Input 1:
  [0,0,0,0],
  [0,1,0,1],
  [0,0,0,0]

"""
def find_paths(arr):
    dfs = []
