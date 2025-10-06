```
https://leetcode.com/problems/path-sum/description/

Step1: add element to dfs and add current node value to the sum
step 2: if node visited remove fromdfs and substract from sum
step 3: if leaf node and sum== target retrun true
else false
```

<img width="657" height="846" alt="image" src="https://github.com/user-attachments/assets/5614a0df-3752-44ea-b0fe-66168bbcf43b" />

```python
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def hasPathSum(self, root: Optional[TreeNode], targetSum: int) -> bool:
        if root == None:
            return False
        dfs = []
        visited = []
        sm = 0
        dfs.append(root)
        while len(dfs)>0:
            node = dfs[-1]
            if node in visited:
                del dfs[-1]
                sm-=node.val
                continue
            sm+=node.val
            if sm == targetSum and node.left is None and node.right is None:
                return True
            if node.left:
                dfs.append(node.left)
            if node.right:
                dfs.append(node.right)
            visited.append(node)
        return False
```        
