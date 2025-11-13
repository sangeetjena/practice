```
https://leetcode.com/problems/binary-tree-level-order-traversal-ii/

Given the root of a binary tree, return the bottom-up level order traversal of its nodes' values.
 (i.e., from left to right, level by level from leaf to root).

Note: similar to level order, but append the result at begining of result list.
```
<img width="382" height="589" alt="image" src="https://github.com/user-attachments/assets/0f29053d-f12c-4e7b-bc7c-b0e3c791c7ae" />


```python
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
```        
        
