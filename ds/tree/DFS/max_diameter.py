"""
https://leetcode.com/problems/diameter-of-binary-tree/

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
            return max(maxDiameter,left+right)
        else:
            return  max(maxDiameter,left+right), 1 + max(left, right)
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        return self.dfs(root, root,0)
        
        
