```
https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/

Given the root of a binary tree, return the zigzag level order traversal of its nodes' values. 
(i.e., from left to right, then right to left for the next level and alternate between).
```
<img width="350" height="587" alt="image" src="https://github.com/user-attachments/assets/444d671c-e1d2-44c7-b2f9-e0e660b8b7ef" />


```python
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
from collections import deque
class Solution:
    def zigzagLevelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        if root == None:
            return []
        queue = deque([root])
        res = []
        cnt = 0
        while len(queue)>0:
            q_len = len(queue)
            temp_lst = []
            for i in range(q_len):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
                temp_lst.append(node.val)
            # for odd levle reversed the list and store.
            if cnt%2!=0:
                temp_lst = temp_lst[::-1]
            cnt+=1
            res.append(temp_lst)
        return res
```
                
