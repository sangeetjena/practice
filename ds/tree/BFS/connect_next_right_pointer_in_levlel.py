"""
https://leetcode.com/problems/populating-next-right-pointers-in-each-node/description/

Note: same as level traversal, at each level store previous node and point it next to current node.
"""

# Definition for a Node.
class Node:
    def __init__(self, val: int = 0, left: 'Node' = None, right: 'Node' = None, next: 'Node' = None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next
"""
from collections import deque
class Solution:
    def connect(self, root: 'Optional[Node]') -> 'Optional[Node]':
        if root == None:
            return root
        queue = deque([root])
        while len(queue):
            ln = len(queue)
            prev = None
            node = None
            for i in range(ln):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
                if prev:
                    prev.next = node
                prev = node
            node.next = None
        return root

        
