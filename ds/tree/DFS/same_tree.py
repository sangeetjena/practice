"""
https://leetcode.com/problems/same-tree/solutions/4782659/beats-100-users-c-java-python-javascript-explained/

"""

class Solution:
    def isSameTree(self, p: TreeNode, q: TreeNode) -> bool:
        if not p and not q:
            return True
        if not p or not q:
            return False
        return p.val == q.val and self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)


==================
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        if p is None and q is None:
            return True
        if p is None or q is None:
            return False
        dfs = []
        visited = []
        dfs.append(p)
        dfs.append(q)
        while len(dfs)>0:
            a = dfs[-1]
            b = dfs[-2]
            if a.val != b.val:
                return False
            if a in visited:
                del dfs[-1]
                del dfs[-1]
                continue
            if (a.left is None and b.left is not None) or (a.left is not None and b.left is  None) or (a.right is None and b.right is not None) or (a.right is not None and b.right is None):
                return False
            if a.left:
                dfs.append(a.left)
                dfs.append(b.left)
            if a.right:
                dfs.append(a.right)
                dfs.append(b.right)


            visited.append(a)
            visited.append(b)
        return True
