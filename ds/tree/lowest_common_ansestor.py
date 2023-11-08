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


*** Extension: Find the Lowest Common Ancestor of Tree (instead of BST) ***

"""
class tree:
    def __init__(self, val, left, right):
        self.value = val
        self.left = left
        self.right = right

def lowest_cmmon_ansestor(node, l , r):
    if node == None:
        return False
    if node.value == l or node.value == r:
        return node
    left = lowest_cmmon_ansestor(node.left, l , r)
    right = lowest_cmmon_ansestor(node.right, l , r)
    # if left is null then right has value else Null, if it has value then that will be the node else it will return  null -> not got value
    if left == False: return right
    if right == False: return left
    # if found both the side then update node to current node.
    return node


 # create tree and pass it to the above function to calculate lca
h7 = tree(7, None, None)
h6 = tree(6, None, h7)
h1 = tree(1, None, None)
h5 = tree(5, h1, h6)
h15 = tree(15, None, None)
h30 = tree(30, None, None)
h20 = tree(20, h15, h30)
h10 = tree(10, h5, h20)

print(lowest_cmmon_ansestor(h10, 6,7).value)

