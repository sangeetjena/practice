```
https://leetcode.com/problems/path-sum-ii/

Given the root of a binary tree and an integer targetSum, return all root-to-leaf paths where the sum of the node values in the path equals targetSum. Each path should be returned as a list of the node values, not node references.

A root-to-leaf path is a path starting from the root and ending at any leaf node. A leaf is a node with no children.

Note: similar to path sum, only difference is storing all matching path to temp path and add to final path.

```

<img width="616" height="815" alt="image" src="https://github.com/user-attachments/assets/c3ba1fd4-6558-4776-9923-3cfe0ed82354" />


```python

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
import copy
class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> List[List[int]]:
        if root == None:
            return []
        all_path = []
        sm = 0
        dfs = []
        temp_path = []
        visited = []
        dfs.append(root)
        while len(dfs)>0:
            node = dfs[-1]
            if node in visited:
                del dfs[-1]
                del temp_path[-1]
                sm-=node.val
                continue
            sm+=node.val
            temp_path.append(node.val)
            # if i got a lead node and target is matching then one match path i found.
            if sm == targetSum and node.left is None and node.right is None:
                if len(temp_path)>0:
                    all_path.append(copy.deepcopy(temp_path))
            if node.left:
                dfs.append(node.left)
            if node.right:
                dfs.append(node.right)
            visited.append(node)
        return all_path
```                
            


        
