"""
https://leetcode.com/problems/binary-tree-level-order-traversal-ii/

Note: similar to level order, but append the result at begining of result list.
"""
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
from collections import deque
class Solution:
    def levelOrderBottom(self, root: Optional[TreeNode]) -> List[List[int]]:
        if root == None:
            return []
        queue = deque([root])
        res = []
        while len(queue)>0:
            curr_len = len(queue)
            curr_lst = []
            for i in range(curr_len):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
                curr_lst.append(node.val)
            res = [curr_lst] + res
        return res
        
        
