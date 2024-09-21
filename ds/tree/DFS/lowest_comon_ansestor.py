"""
https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/

Given a binary search tree (BST), find the lowest common ancestor (LCA) node of two given nodes in the BST.

According to the definition of LCA on Wikipedia: “The lowest common ancestor is defined between two nodes p and q as the lowest node in T that has both p and q as descendants (where we allow a node to be a descendant of itself).”

 

Example 1:


Input: root = [6,2,8,0,4,7,9,null,null,3,5], p = 2, q = 8
Output: 6
Explanation: The LCA of nodes 2 and 8 is 6.


"""
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        if root is None:
            return False
        if root.val in [p.val, q.val]:
            return root
        
        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)
        # if both the node available then return lowest node found and then return node to its parent node
        if left and right:
            return root
        # if in above cond not executed then node might exists in left or right.
        # so 2 condition possible 1- both node found in the one child node 
        #.                        2- both node exists in one side so the 1st matching node will return.
        # if no further left and right node found that means either both the node found in current node left or right side or both the node was existing in one side of left or riht node.
        if left:
            return left
        if right:
            return right
        # as it is guarented that nodes will be avilable in the tree so no need to return false

        
