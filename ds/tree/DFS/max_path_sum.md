```
https://leetcode.com/problems/binary-tree-maximum-path-sum/

A path in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge
connecting them. A node can only appear in the sequence at most once. Note that the path does not need to pass through the root.

The path sum of a path is the sum of the node's values in the path.

Given the root of a binary tree, return the maximum path sum of any non-empty path.

Note: same as max diameter, only diff is return max sum to parent only positive no else return 0
also max path possible along diameter, so find max sum along diameter of the tree.
```
<img width="740" height="742" alt="image" src="https://github.com/user-attachments/assets/176f96ed-4d02-429f-af67-3a8c0211f0fd" />

```python
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
        # same as max diameter, only diff is return max sum to parent only positive number else return 0
        return max(root.val + max(left , right), 0)

    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        dp = [-9999999]
        self.dfs(root, dp)
        return dp[0]
        
```
