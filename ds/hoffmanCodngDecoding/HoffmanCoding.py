class Node:
    def __init__(self):
        self.weight = None
        self.char = None
        self.right = None
        self.left = None
        self.huf=None
class HoffmanCoding:
    def __init__(self):
        self.tree=[]
        self.encode={}
        self.occurence={}
        self.waightedOccurence=[]

    def createNode(self,char,weight,addrL,addrR):
        obj=Node()
        obj.weight=weight
        obj.char=char
        obj.right=addrR
        obj.left=addrL
        return obj

    def createEnCode(self,words):
        for chr in words:
            if chr in self.occurence.keys():
                self.occurence[chr]+=1
            else:
                self.occurence[chr]=1
        #build tree from the occurence list
        for key in self.occurence.keys():
            self.waightedOccurence.append({'key':key,'value':self.occurence[key]})
        #sort the weightedOccurence
        for i in range(0,self.waightedOccurence.__len__()):
            smalest=self.waightedOccurence[i]['value']
            index=i

            for y in range(i+1,self.waightedOccurence.__len__()):
                if(smalest>self.waightedOccurence[y]['value']):
                    smalest=self.waightedOccurence[y]['value']
                    index=y
            if(index!=i):
                tempvalue=self.waightedOccurence[index]
                self.waightedOccurence[index]=self.waightedOccurence[i]
                self.waightedOccurence[i]=tempvalue
        print(self.waightedOccurence)
        #build tree
        for i in range(0,self.waightedOccurence.__len__()):
            node=self.createNode(self.waightedOccurence[i]['key'],self.waightedOccurence[i]['value'],None,None)
            self.tree.append(node)
        self.buildEncodedTree()
        self.traverseTree(self.tree[0],'')
    def buildEncodedTree(self):

        while (self.tree.__len__()>1):
            x=self.tree[0].weight + self.tree[1].weight
            obj=self.createNode('#',x,self.tree[0],self.tree[1])
            self.tree[0].huf=0
            del self.tree[0]
            self.tree[0].huf=1
            del self.tree[0]
            # place this new node into the correct position by waight
            for i in range(0, self.tree.__len__()):
                if self.tree[i].weight > x:
                    templst=self.tree[i:]
                    del self.tree[i:]
                    self.tree.append(obj)
                    self.tree=self.tree+templst
                    break
                else:
                    self.tree.append(obj)
                    break
            if(self.tree.__len__()==0):
                self.tree.append(obj)
    def traverseTree(self,node,val=''):
        newval=''
        if node.huf!=None:
            newval=val+str(node.huf)
        if node.left:
            self.traverseTree(node.left,newval)
        if node.right:
            self.traverseTree(node.right,newval)
        if (not node.right and not node.left):
            self.encode[node.char]=newval







hof = HoffmanCoding()
hof.createEnCode("geegsforgeegs")
print(hof.encode)
