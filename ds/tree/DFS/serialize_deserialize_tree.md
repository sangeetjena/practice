```
https://leetcode.com/problems/serialize-and-deserialize-binary-tree/

Serialization is the process of converting a data structure or object into a sequence of bits so that it can be stored in a file or memory buffer, or transmitted across a network connection link to be reconstructed later in the same or another computer environment.

Design an algorithm to serialize and deserialize a binary tree. There is no restriction on how your serialization/deserialization algorithm should work. You just need to ensure that a binary tree can be serialized to a string and this string can be deserialized to the original tree structure.

Clarification: The input/output format is the same as how LeetCode serializes a binary tree. You do not necessarily need to follow this format, so please be creative and come up with different approaches yourself.


Note: pre-order  then recurrsion dfs .
```
<img width="483" height="430" alt="image" src="https://github.com/user-attachments/assets/d100a9ed-4c0e-4bf4-a3c3-70b0a8dc2761" />


```python
# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None
i = 0
class Codec:
    
    def serialize(self, root):
        if root == None:
            return "N"
        return str(root.val) + "," + self.serialize(root.left) + "," + self.serialize(root.right)

    def deserialize(self, data):
        lst = data.split(",")
        global i
        i=0
        def dfs():
            global i
            if lst[i] == "N":
                return None
            nd = TreeNode(int(lst[i]))
            i+=1
            nd.left = dfs()
            i+=1
            nd.right = dfs()
            return nd
        return dfs()
```            
