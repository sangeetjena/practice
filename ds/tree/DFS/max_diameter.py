"""
https://leetcode.com/problems/diameter-of-binary-tree/

Note: for each node while returning to it parent node return the max diameter sofar and max defth from current node.
on root node check if max diameter is greater than current diameter then return max diameter.
"""


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def dfs(self, node, root, maxDiameter):
        if node == None:
            return 0,0
        lmaxDiameter, left = self.dfs(node.left, root, maxDiameter) 
        rmaxDiameter, right = self.dfs(node.right, root, maxDiameter)
        maxDiameter = max(lmaxDiameter, rmaxDiameter, maxDiameter)
        if node == root:
            # at the root if in its child( left and right) branch  max diameter would have formed then return that.
            return max(maxDiameter,left+right)
        else:
            # max condition to check if this would be the root node then what would be the max diameter 
            return  max(maxDiameter,left+right), 1 + max(left, right)
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        return self.dfs(root, root,0)
        
        
