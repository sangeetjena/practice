"""
https://leetcode.com/problems/binary-tree-maximum-path-sum/

Note: same as max diameter, only diff is return max sum to parent only positive no else return 0
"""
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def dfs(self, root, dp):
        if root is None:
            return 0
        left = self.dfs(root.left,dp)
        right = self.dfs(root.right,dp)
        dp[0] = max(dp[0], root.val + left + right)
        # same as max diameter, only diff is return max sum to parent only positive no else return 0
        return max(root.val + max(left , right), 0)

    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        dp = [-9999999]
        self.dfs(root, dp)
        return dp[0]
        
