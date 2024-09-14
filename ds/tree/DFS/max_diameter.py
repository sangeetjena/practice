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
    def dfs(self, node, dp):
        if node == None:
            return 0
        left = self.dfs(node.left, dp) 
        right = self.dfs(node.right, dp)
        # what is the max diameter at this node
        dp[0] = max(dp[0],left+right)
        # return to parent node what is the max depth sofar
        return 1 + max(left, right)
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        dp = [0]
        self.dfs(root, dp)
        return dp[0]
        
        
