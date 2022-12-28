class tree():
    def __init__(self, val):
        self.value = val
        self.left = None
        self.right = None

class diameterOfTree():
    def __init__(self):
        self.leftmaxdepth=0
        self.rightmaxdepth=0
        self.stack=[]
        self.lstack=[]
        self.rstack=[]

    def maxdiameter(self, root):
        self.stack.append(root)
        maxlen = 0
        maxlenL = 0
        maxlenR = 0
        templen = 0
        node = root
        while len(self.stack)>0:
            print(node.value)
            if node.left != None and node not in self.lstack:
                self.lstack.append(node)
                self.stack.append(node)
                node = node.left
                templen+=1
                continue
            elif node.right != None and node not in self.rstack:
                self.rstack.append(node)
                self.stack.append(node)
                node = node.right
                templen+=1
                continue
            else:
                node = self.stack[-1]
                del self.stack[-1]
                if maxlen < templen:
                    maxlen = templen
                print(templen)
                templen -= 1
                if node == root and node not in self.rstack:
                    maxlenL=maxlen
                    maxlen = 0
                    continue
                elif node == root and node in self.rstack:
                    maxlenR = maxlen

        return (maxlenL,maxlenR)


root = tree('a')
obj = tree('b')
obj1 = tree('c')
obj2 = tree('d')
obj3 = tree('e')
obj4 = tree('f')
obj5 = tree('g')
obj6 = tree('k')
obj7 = tree('l')
obj8 = tree('j')
obj9 = tree('h')
obj10 = tree('i')


root.left = obj
root.left.left = obj1
root.left.right = obj2
root.right = obj3
root.left.left.left=obj4
root.left.left.right=obj5
root.left.left.left.left=obj6
root.left.left.left.right=obj7
root.left.right.left=obj9
root.left.right.right=obj10
root.left.right.right.right=obj8


x = diameterOfTree()
ml, mr = x.maxdiameter(root.left)

print(ml,mr)