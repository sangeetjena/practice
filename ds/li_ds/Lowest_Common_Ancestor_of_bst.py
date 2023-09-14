"""
The lowest common ancestor is defined between two nodes v and w as the lowest node in a tree that has both v and w as descendants (where we allow a node to be a descendant of itself).
Given a binary search tree (BST), find the lowest common ancestor (LCA) of two given nodes in the BST.

Given the following Binary Search Tree:
                10
               /  \
              5    20
             /\    /\
            1  6  15 30
                \
                 7
The lowest common ancestor of node 1 and 7 is 5.
The lowest common ancestor of node 1 and 5 is 5.
"""
class Tree:
    def __init__(self, val, left=None, right=None):
        self.val  = val
        self.left = left
        self.right = right

def find_lowest_ancestor(node, s,e):
    if node == None:
        return None
    if(node.val == e or node.val == s):
        print(node.val)
        return True
    left = find_lowest_ancestor(node.left, s, e)
    right = find_lowest_ancestor(node.right, s, e)
    if( left != None and right != None):
        return node.val
    return left if left != None else right

a1 = Tree(1)
a7 = Tree(7)
a6 = Tree(6,None, a7)
a5 = Tree(5,a1,a6)
a15 = Tree(15)
a30 = Tree(30)
a20 = Tree(20,a15,a30)
a = Tree(10, a5, a20)
a10 = Tree(10,a5,a20)

print(find_lowest_ancestor(a10, 1,30))





