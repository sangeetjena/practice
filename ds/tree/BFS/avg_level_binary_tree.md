```
https://leetcode.com/problems/average-of-levels-in-binary-tree/description/

Given the root of a binary tree, return the average value of the nodes on each level in the form of an array.
Answers within 10-5 of the actual answer will be accepted.

Note: same as level order trversal, take count of nodes and sum off all nodes in a level and calculate avg.

```
<img width="854" height="849" alt="image" src="https://github.com/user-attachments/assets/d0d931a0-3d00-40c0-9b9b-2b873299220b" />



```python

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
```     
