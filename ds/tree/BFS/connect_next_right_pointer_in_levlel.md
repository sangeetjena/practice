```
https://leetcode.com/problems/populating-next-right-pointers-in-each-node/description/

You are given a perfect binary tree where all leaves are on the same level, and every parent has two children. The binary tree has the following definition:

struct Node {
  int val;
  Node *left;
  Node *right;
  Node *next;
}
Populate each next pointer to point to its next right node. If there is no next right node, the next pointer should be set to NULL.

Initially, all next pointers are set to NULL.


Note: same as level traversal, at each level store previous node and point it next to current node.
```

<img width="848" height="430" alt="image" src="https://github.com/user-attachments/assets/4b0f1972-3c1e-444b-84fe-4aec8ccc7925" />


```python

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

```
