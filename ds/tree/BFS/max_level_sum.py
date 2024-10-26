"""
https://leetcode.com/problems/maximum-level-sum-of-a-binary-tree/

Note: find sum in each level, from that find max sum 
"""

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
from collections import deque
class Solution:
    def maxLevelSum(self, root: Optional[TreeNode]) -> int:
        if root == None:
            return []
        queue = deque([root])
        maxlevel = 0
        maxsm = - float(maxsize)
        cnt = 1
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
            if maxsm< sm:
                maxsm = sm
                maxlevel = cnt
            cnt+=1
        return maxlevel
        
