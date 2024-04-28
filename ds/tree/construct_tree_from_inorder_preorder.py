"""
Given two integer arrays preorder and inorder where preorder is the preorder traversal of a binary tree
and inorder is the inorder traversal of the same tree, construct and return the binary tree.

Input: preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]
Output: [3,9,20,null,null,15,7]
"""
output = []
def constructTree(preOrder, inOrder):
    if len(preOrder)== 0 or len(inOrder) == 0:
        output.append(None)
        return None
    middleInd =  0
    for i in range(len(inOrder)):
        if (preOrder[0] == inOrder[i]):
            middleInd = i
            break
    output.append(preOrder[0])
    inleft = inOrder[0:middleInd]
    inright = inOrder[middleInd + 1:]
    print("in order",inleft, inright)
    preleft = preOrder[1: len(inleft) + 1]
    preRight = preOrder[len(inleft)+1: ]
    print("pre-order", preleft, preRight)
    print("out", output)

    constructTree(preleft, inleft)
    constructTree(preRight, inright)



preorder = [3,9,20,15,7]
inorder = [9,3,15,20,7]
constructTree(preorder, inorder)
print(output)