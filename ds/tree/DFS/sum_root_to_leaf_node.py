"""
https://leetcode.com/problems/sum-root-to-leaf-numbers/description/

"""
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def sumNumbers(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        dfs = []
        visited = []
        temp_path = []
        total = 0
        dfs.append(root)
        while len(dfs) > 0:
            node = dfs[-1]
            if node in visited:
                del dfs[-1]
                del temp_path[-1]
                continue
            temp_path.append(str(node.val))
            if node.left is None and node.right is None:
                print(temp_path)
                total += int("".join(temp_path))
            if node.left:
                dfs.append(node.left)
            if node.right:
                dfs.append(node.right)
            visited.append(node)
        return total
        
