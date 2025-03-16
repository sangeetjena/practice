"""
https://leetcode.com/problems/count-good-nodes-in-binary-tree/description/?envType=study-plan-v2&envId=leetcode-75

Note:
This problem is similar to the max path sum -2 problem. keep a treack of max value till the node.
ex: as we traverse through the child nodes find the max value till the child, if child value is greater then it is a valid path and update the new maxValue in the recursion call 
       
""""

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    
    def goodNodes(self, root: TreeNode) -> int:
        self.goodNode = 0
        # this problem is similar to the max path sum -2 problem. keep a treack of max value till the node.
        # ex: as we traverse through the child nodes find the max value till the child, if child value is greater then it is a valid path and update the new maxValue in the recursion call 
        def findGoodNodes(root, maxVal):
            if root == None:
                return
            if root.val >= maxVal:
                self.goodNode +=1
            findGoodNodes(root.left, max(root.val, maxVal))
            findGoodNodes(root.right, max(root.val, maxVal))
        findGoodNodes(root,root.val)
        return self.goodNode
