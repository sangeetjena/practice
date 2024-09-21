"""
https://leetcode.com/problems/validate-binary-search-tree/
https://www.youtube.com/watch?v=s6ATEkipzow

Note: in recursion when going to child define it left and right value.
      from root l=-ind and r = +inf. when going to left child only modify right value to parent node value
      and for right child update only left value to present node value.

"""
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        def valid(node, left, right):
            if node is None:
                return True
            if not( node.val > left and node.val < right):
                return False
            # if  (node.val <= left or node.val >= right):
            #     return False
            # if child going to left it boundary should be l= parent left  and rihgt = prent val
            # if child going to right it boundary should be r = parent right  and left = prent val
            return valid(node.left, left, node.val) and valid(node.right, node.val, right)
        return valid(root, float("-inf"), float("inf"))
                
