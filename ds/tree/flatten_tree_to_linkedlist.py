"""

"""
prev = None
head = None
class tree():
    def __init__(self, val, left, right):
        self.value = val
        self.left = left
        self.right = right


def flatten_tree(node):
    global prev, head
    if node == None:
        return
    # traversing left and right then changing link sothat we need not to memorize right or left node.
    # Note: for in order (l,r) , pre order traversal (right) we need to store before changing the link
    # in order to convert a tree to a linkedlist cut all right node and put it into left side.
    flatten_tree(node.left)
    flatten_tree(node.right)
    if prev != None:
        node.left = prev
        prev.right = None
    prev = node


def print_linkedlist():
    curr = prev
    while curr!=None:
        print(curr.value)
        curr = curr.left

h7 = tree(7, None, None)
h6 = tree(6, None, h7)
h1 = tree(1, None, None)
h5 = tree(5, h1, h6)
h15 = tree(15, None, None)
h30 = tree(30, None, None)
h20 = tree(20, h15, h30)
h10 = tree(10, h5, h20)

flatten_tree(h10)
print_linkedlist()