"""
The diameter/width of a tree is defined as the number of nodes on the longest path between two end nodes.

The diagram below shows two trees each with a diameter of nine, the leaves that form the ends of the longest path are shaded (note that there is more than one path in each tree of length nine, but no path longer than nine nodes).

                10
               /  \
              5    20
             /\    /\
            1  6  15 30
                \
                 7
The longest diameter : 7-6-5-10-20-30
"""
class tree():
    def __init__(self, val, left, right):
        self.value = val
        self.left = left
        self.right = right

def find_max_diameter_of_tree(node, maxlen):
    if node == None:
        return 0
    l = find_max_diameter_of_tree(node.left, maxlen)
    r = find_max_diameter_of_tree(node.right, maxlen)
    maxlen[-1] = max(maxlen[-1], 1 + l + r)
    return 1 + max(l, r)

h7 = tree(7, None, None)
h6 = tree(6, None, h7)
h1 = tree(1, None, None)
h5 = tree(5, h1, h6)
h15 = tree(15, None, None)
h30 = tree(30, None, None)
h20 = tree(20, h15, h30)
h10 = tree(10, h5, h20)

maxlen = [0]
find_max_diameter_of_tree(h10,maxlen)
print(maxlen)
