"""
1325. Delete Leaves With a Given Value
Medium
2K
35
company
Amazon
company
Google
Oracle
Given a binary tree root and an integer target, delete all the leaf nodes with value target.

Note that once you delete a leaf node with value target, if its parent node becomes a leaf node and has the value target, it should also be deleted (you need to continue doing that until you cannot).



Example 1:



Input: root = [1,2,3,2,null,2,4], target = 2
Output: [1,null,3,null,4]
Explanation: Leaf nodes in green with value (target = 2) are removed (Picture in left).
After removing, new nodes become leaf nodes with value (target = 2) (Picture in center).

"""



# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def removeLeafNodes(self, root: Optional[TreeNode], target: int) -> Optional[TreeNode]:
        if root == None:
            return None

        left = self.removeLeafNodes(root.left, target)
        right = self.removeLeafNodes(root.right, target)
        print(root.val)
        print(root.val, left, right)
        if left and left.val == "null":
            root.left = None
        if right and right.val == "null":
            root.right == None
        if root.left == None and root.right == None and root.val == target:
            root.val = "null"
            return root
        return root