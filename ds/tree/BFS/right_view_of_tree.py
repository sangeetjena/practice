"""
https://leetcode.com/problems/binary-tree-right-side-view/

Note: similar to the level order traversal, only difference is capture the last most element to extream right and preserve.
"""
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
from collections import deque
class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        if root == None:
            return []
        out = []
        queue = deque([root])
        while len(queue)>0:
            
            q_len = len(queue)
            node = None
            for i in range(q_len):
                node = queue.popleft()
                print(node)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            # capturuing only the last element in the level.
            out.append(node.val)
        return out

        
