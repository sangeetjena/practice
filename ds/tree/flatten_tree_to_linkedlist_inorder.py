"""
Note: for in order traversal capture previous and current righ pointer because child
process will change the right of root.
then 1- perform operation
    parse 2- left 3- right

"""
from typing import Optional

prev = None
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def flatten(self, root: Optional[TreeNode]) -> None:
        global prev
        right = None
        """
        Do not return anything, modify root in-place instead.
        """
        if root == None:
            return None
        right = root.right
        if prev == None:
            prev = root
        else:
            prev.right = root
            prev.left =None
            prev = root

        self.flatten(root.left)
        self.flatten(right)