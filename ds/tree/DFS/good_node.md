```
https://leetcode.com/problems/count-good-nodes-in-binary-tree/description/?envType=study-plan-v2&envId=leetcode-75

Given a binary tree root, a node X in the tree is named good if in the path from root to X there are no nodes with a value greater than X.

Return the number of good nodes in the binary tree.



Note:
This problem is similar to the max path sum -2 problem. keep a treack of max value till the node.
ex: as we traverse through the child nodes find the max value till the child, if child value is greater then it is a valid path and update the new maxValue in the recursion call 

```
<img width="717" height="759" alt="image" src="https://github.com/user-attachments/assets/f8a22ea1-2bf4-4560-8cee-2174f5760696" />


```python

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
```
