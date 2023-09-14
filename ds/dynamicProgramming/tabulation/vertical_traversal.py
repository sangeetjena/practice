"""
print all nodes in same index
"""
class tree:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
def print_vertical_nodes(node,level,dict):
    if node == None:
        return
    if not level in dict.keys():
        dict[level] = []
    dict[level].append(node.val)
    print(dict[level])
    print_vertical_nodes(node.left, level -1, dict)
    print_vertical_nodes(node.right, level +1, dict)
    return dict


n8 = tree(8)
n11 = tree(11)
n13 = tree(13)
n7 = tree(7,None,n8)
n3 = tree(3)
n5 = tree(5,n3)
n12 = tree(12,n11,n13)
n6 = tree(6, n5,n7)
n0 = tree(10, n6, n12)

print(print_vertical_nodes(n0,0,{}))







