class tree:
    def __init__(self, val, left, right):
        self.val = val
        self.left = left
        self.right = right


def parse(node, level, printlevel):
    if node == None:
        return
    if printlevel == level:
        print(node.val)
    left = parse(node.left, level + 1, printlevel)
    right = parse(node.right, level + 1, printlevel)


h7 = tree(7, None, None)
h6 = tree(6, None, h7)
h1 = tree(1, None, None)
h5 = tree(5, h1, h6)
h15 = tree(15, None, None)
h30 = tree(30, None, None)
h20 = tree(20, h15, h30)
h10 = tree(10, h5, h20)

parse(h10, 0, 2)