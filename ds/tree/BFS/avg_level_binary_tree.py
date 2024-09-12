"""
https://leetcode.com/problems/average-of-levels-in-binary-tree/description/

Note: same as level order trversal, take count of nodes and sum off all nodes in a level and calculate avg.

"""

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
from collections import deque
class Solution:
    def averageOfLevels(self, root: Optional[TreeNode]) -> List[float]:
        queue = deque([root])
        res = []
        while len(queue)>0:
            q_len = len(queue)
            sm = 0
            for i in range(q_len):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
                sm+=node.val
            res.append(sm/q_len)
        return res
        
