"""
https://leetcode.com/problems/longest-zigzag-path-in-a-binary-tree/description/?envType=study-plan-v2&envId=leetcode-75

Note:


"""
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
            # why other side 0 ?  because if we will mode in the same direction that is not a valid mode so nullify that move. an any move after that will be considered as a fresh move from the begining.
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

        
        
