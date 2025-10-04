```
https://leetcode.com/problems/longest-zigzag-path-in-a-binary-tree/description/?envType=study-plan-v2&envId=leetcode-75

You are given the root of a binary tree.

A ZigZag path for a binary tree is defined as follow:

Choose any node in the binary tree and a direction (right or left).
If the current direction is right, move to the right child of the current node; otherwise, move to the left child.
Change the direction from right to left or from left to right.
Repeat the second and third steps until you can't move in the tree.
Zigzag length is defined as the number of nodes visited - 1. (A single node has a length of 0).

Return the longest ZigZag path contained in that tree.

Note:


```
<img width="643" height="500" alt="image" src="https://github.com/user-attachments/assets/05132a1a-c638-426c-9d5e-4c40214c9567" />

<img width="645" height="569" alt="image" src="https://github.com/user-attachments/assets/9cdafd98-4168-470e-b7d5-a750aaf33621" />

```python
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def longestZigZag(self, root: Optional[TreeNode]) -> int:
        self.max_len = 0
        def dfs( root, left, right):
            self.max_len = max(self.max_len, left, right)

            #check if left side node is available or not
            # increment value by one with other side (if left add right value +1) and make the other side 0
            # why other side 0 ?  at current node two condution possible 1- continue to the previous sequence , condition 2: taking current node as starting point.
            #                     so if condition 1: then if we are moving left then it will be continuation to right level and vice versa
            #                     for condition 2: current node with start with level 0. so make the other side of the direction we are moving as 0.
            # we are using max_len so for upto that point we already would have calculated the max mode.
            if root.left:
                dfs(root.left, right+1, 0)
            if root.right:
                dfs(root.right,0, left+1)
        dfs(root, 0,0)
        return self.max_len



-- bruite force 
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def __init__(self):
        self.maxlen = 0
    def longestPath(self, root, direction, len):
        if root == None:
            return len-1
        if direction == "left":
            return self.longestPath(root.right, "right", len+1)
        if direction == "right":
            return self.longestPath(root.left, "left", len+1)
        

    def longestZigZag(self, root: Optional[TreeNode]) -> int:
        if root == None:
            return 0
        ll = self.longestPath(root.left, "left", 1)
        lr = self.longestPath(root.right, "right", 1)
        self.maxlen = max(self.maxlen, ll, lr)
        self.longestZigZag(root.left)
        self.longestZigZag(root.right)
        return self.maxlen
```
        
        
