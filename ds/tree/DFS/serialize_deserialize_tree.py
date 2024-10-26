"""
https://leetcode.com/problems/serialize-and-deserialize-binary-tree/


Note: pre-order  then recurrsion dfs .
"""
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
            
