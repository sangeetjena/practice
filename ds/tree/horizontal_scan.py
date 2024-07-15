"""
scan a tree horizontally
https://leetcode.com/problems/binary-tree-level-order-traversal/
"""


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        if root == None:
            return []
        parentlist = [root]
        templist = []
        totallist = [[root.val]]
        while len(parentlist)>0:
            for root in parentlist:
                if root.left != None:
                    templist.append(root.left)
                if root.right != None:
                    templist.append(root.right)
            if len(templist) > 0:
                totallist.append([node.val for node in templist])
            parentlist = templist
            templist = []
        return totallist

        

"""
class tree():
    def __init__(self, val, left, right):
        self.value = val
        self.left = left
        self.right = right

horizontal = {}
def scan_horizontally(node, level):
    global horizontal
    if node == None:
        return
    if level in horizontal.keys():
        horizontal[level].append(node.value)
    else:
        horizontal[level] = [node.value]
    scan_horizontally(node.left,level + 1)
    scan_horizontally(node.right, level + 1)

h7 = tree(7, None, None)
h6 = tree(6, None, h7)
h1 = tree(1, None, None)
h5 = tree(5, h1, h6)
h15 = tree(15, None, None)
h30 = tree(30, None, None)
h20 = tree(20, h15, h30)
h10 = tree(10, h5, h20)

scan_horizontally(h10, 0)
print(horizontal)
"""
