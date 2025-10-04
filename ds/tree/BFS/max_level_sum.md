```
https://leetcode.com/problems/maximum-level-sum-of-a-binary-tree/

Given the root of a binary tree, the level of its root is 1, the level of its children is 2, and so on.

Return the smallest level x such that the sum of all the values of nodes at level x is maximal.

Note: find sum in each level, from that find max sum 
```
<img width="584" height="464" alt="image" src="https://github.com/user-attachments/assets/60abf13c-2682-4bab-bd00-c4889389f84d" />


```python

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
```   
