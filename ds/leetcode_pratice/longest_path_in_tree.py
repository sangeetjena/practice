# Python3 program to find the length of longest
# path with same values in a binary tree.

# Helper function that allocates a
# new node with the given data and
# None left and right pointers.
class newNode:
    def __init__(self, data):
        self.val = data
        self.left = self.right = None


# Function to print the longest path
# of same values
def length(node, ans):
    if (not node):
        return 0


    # Recursive calls to check for subtrees
    left = length(node.left, ans)
    right = length(node.right, ans)

    # Variables to store maximum lengths
    # in two directions
    Leftmax = 0
    Rightmax = 0

    # If curr node and it's left child has same value
    if (node.left and node.left.val == node.val):
        Leftmax += left + 1

# If curr node and it's right child has same value
    if (node.right and node.right.val == node.val):
        Rightmax += right + 1

    ans[0] = max(ans[0], Leftmax + Rightmax)
    return max(Leftmax, Rightmax)


# Driver function to find length of
# longest same value path
def longestSameValuePath(root):
    ans = [0]
    length(root, ans)
    return ans[0]

# Driver code
if __name__ == '__main__':

    # Let us construct a Binary Tree
    #	 4
    #	 / \
    # 4 4
    # / \ \
    # 4 9 5
    root = None
    root = newNode(4)
    root.left = newNode(4)
    root.right = newNode(4)
    root.left.left = newNode(4)
    root.left.right = newNode(9)
    root.right.right = newNode(5)
    print(longestSameValuePath(root))

# This code is contributed by PranchalK
