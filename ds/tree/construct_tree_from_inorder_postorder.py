"""
Given two integer arrays inorder and postorder where inorder is the inorder traversal of a binary tree and postorder is the postorder traversal of the same tree,
construct and return the binary tree.

Input: inorder = [9,3,15,20,7], postorder = [9,15,7,20,3]
Output: [3,9,20,null,null,15,7]
"""


class BuildTree:
    head = None

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

    def constructTree(self, inOder, postOrder):
        if len(inOder) == 0 or len(postOrder) == 0:
            return None
        node = BuildTree(postOrder[-1])
        if self.head is None:
            self.head = node
        print(inOder, postOrder)
        mid = inOder.index(postOrder[-1])
        node.left = self.constructTree(inOder[: mid], postOrder[: mid])
        node.right = self.constructTree(inOder[mid + 1:], postOrder[mid: len(postOrder) - 1])
        return node

    def parseTree(self, node):
        if node is None:
            return None
        print(node.val)
        self.parseTree(node.left)
        self.parseTree(node.right)


inorder = [9, 3, 15, 20, 7]
postorder = [9, 15, 7, 20, 3]
# Output: [3,9,20,null,null,15,7]
obj = BuildTree(0)
obj.constructTree(inorder, postorder)
obj.parseTree(obj.head)
