```
https://leetcode.com/problems/sum-root-to-leaf-numbers/description/

You are given the root of a binary tree containing digits from 0 to 9 only.

Each root-to-leaf path in the tree represents a number.

For example, the root-to-leaf path 1 -> 2 -> 3 represents the number 123.
Return the total sum of all root-to-leaf numbers. Test cases are generated so that the answer will fit in a 32-bit integer.

A leaf node is a node with no children.



```

<img width="528" height="869" alt="image" src="https://github.com/user-attachments/assets/31566c08-2cdb-4192-8a60-cb2b90e5f19e" />


```python
    
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def sumNumbers(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        dfs = []
        visited = []
        temp_path = []
        total = 0
        dfs.append(root)
        while len(dfs) > 0:
            node = dfs[-1]
            if node in visited:
                del dfs[-1]
                del temp_path[-1]
                continue
            temp_path.append(str(node.val))
            if node.left is None and node.right is None:
                print(temp_path)
                total += int("".join(temp_path))
            if node.left:
                dfs.append(node.left)
            if node.right:
                dfs.append(node.right)
            visited.append(node)
        return total
        
```
