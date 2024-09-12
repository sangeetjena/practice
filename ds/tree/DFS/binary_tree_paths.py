"""
https://leetcode.com/problems/binary-tree-paths/

"""
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def binaryTreePaths(self, root: Optional[TreeNode]) -> List[str]:
        dfs = []
        all_path = []
        visited = []
        dfs.append(root)
        temp_path = []
        while len(dfs)>0:
            node = dfs[-1]
            if node in visited:
                del dfs[-1]
                del temp_path[-1]
                continue
            temp_path.append(str(node.val))
            print(temp_path)
            if node.left is None and node.right is None:
                all_path.append(copy.deepcopy("->".join(temp_path)))
            if node.left:
                dfs.append(node.left)
            if node.right:
                dfs.append(node.right)
            visited.append(node)
        return all_path
        
