"""
Binary Tree Maximum Path Sum:
A path in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge connecting them. A node can only appear in the sequence at most once. Note that the path does not need to pass through the root.

The path sum of a path is the sum of the node's values in the path.

Given the root of a binary tree, return the maximum path sum of any non-empty path.

Input: root = [1,2,3]
Output: 6
Explanation: The optimal path is 2 -> 1 -> 3 with a path sum of 2 + 1 + 3 = 6.
"""
from typing import Optional

# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right



class Solution:
    def __init__(self):
        self.max_val=-9999
    def dfs(self, root):
        if(root is None):
            return 0
        left = self.dfs(root.left)
        right = self.dfs(root.right)
        # 
        if self.max_val < (root.val + max(left, 0) + max(right,0)):
            self.max_val = (root.val + max(left, 0) + max(right,0))
        return root.val + max(left, right, 0)
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        self.max_val=-9999
        self.dfs(root)
        return self.max_val