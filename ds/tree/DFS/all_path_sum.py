"""
https://leetcode.com/problems/path-sum-ii/

Note: similar to path sum, only difference is storing all matching path to temp path and add to final path.

"""

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
import copy
class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> List[List[int]]:
        if root == None:
            return []
        all_path = []
        sm = 0
        dfs = []
        temp_path = []
        visited = []
        dfs.append(root)
        while len(dfs)>0:
            node = dfs[-1]
            if node in visited:
                del dfs[-1]
                del temp_path[-1]
                sm-=node.val
                continue
            sm+=node.val
            temp_path.append(node.val)
            # if i got a lead node and target is matching then one match path i found.
            if sm == targetSum and node.left is None and node.right is None:
                if len(temp_path)>0:
                    all_path.append(copy.deepcopy(temp_path))
            if node.left:
                dfs.append(node.left)
            if node.right:
                dfs.append(node.right)
            visited.append(node)
        return all_path
                
            


        
