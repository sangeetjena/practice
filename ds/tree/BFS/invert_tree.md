```
https://leetcode.com/problems/invert-binary-tree/description/
Given the root of a binary tree, invert the tree, and return its root.
Example 1:
Input: root = [4,2,7,1,3,6,9]
Output: [4,7,2,9,6,3,1]

Note: same as bfs, only difference is while pushing to queue push right before left.

```
<img width="526" height="595" alt="image" src="https://github.com/user-attachments/assets/2c54853a-4019-47d3-a3a7-202b2aaaf99d" />


```python
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
from collections import deque
class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        if root is None:
            return root
        queue = deque([root])
        while len(queue)>0:
            ln = len(queue)
            for i in range(ln):
                node = queue.popleft()
                # to revert tree push right sub tree before left , tree will be inverted.
                if node.right:
                    queue.append(node.right)
                if node.left:
                    queue.append(node.left)
                node.left, node.right = node.right, node.left
        return root
```

        
