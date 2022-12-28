
def parseChieldTree(currentparentnode,currentchildnode):
    childStack=[currentchildnode]
    parentStack=[currentparentnode]
    leftVisitedNode=[]
    rightVisitedNode=[]
    while(len(childStack)!=0):
        if currentparentnode.value!=currentchildnode.value or currentparentnode is None:
            return 0
        if currentchildnode.left is not None and currentchildnode not in leftVisitedNode:
            leftVisitedNode.append(currentchildnode)
            currentchildnode=currentchildnode.left
            currentparentnode=currentparentnode.left
            childStack.append(currentchildnode)
            parentStack.append(currentparentnode)
        elif currentchildnode.right is not None and currentchildnode not in rightVisitedNode:
            rightVisitedNode.append(currentchildnode)
            currentchildnode=currentchildnode.right
            currentparentnode=currentparentnode.right
            childStack.append(currentchildnode)
            parentStack.append(currentparentnode)
        else:
            currentchildnode=childStack[-1]
            currentparentnode=parentStack[-1]
            childStack=childStack[0:-1]
            parentStack=parentStack[0:-1]
    return 1

    
def findSubTree(childnode,parentnode):
    chieldTree = []
    stack = []
    leftvisitednode = []
    rightvisitednode = []
    currentparentnode=parentnode
    currentchildnode=childnode
    stack.append
    while (len(stack)!=0):
        allfound=0
        if currentparentnode.left!=None and currentparentnode.left not in leftvisitednode:
            leftvisitednode.append(currentparentnode)
            currentparentnode=currentparentnode.left
            stack.append(currentparentnode)
            if(currentparentnode.val==currentchildnode.val):
                allfound=parseChieldTree(currentparentnode,currentchildnode)
            if (allfound==1):
                break;
            continue
        elif currentparentnode.right!=None and currentparentnode.right not in rightvisitednode:
            rightvisitednode.append(currentparentnode)
            currentparentnode = currentparentnode.right
            stack.append(currentparentnode)
            if (currentparentnode.val == currentchildnode.val):
                parseChieldTree(currentparentnode, currentchildnode)
            if (allfound==1):
                break;
            continue
        else:
            currentparentnode=stack[-1]
            stack=stack[0:-1]




̉