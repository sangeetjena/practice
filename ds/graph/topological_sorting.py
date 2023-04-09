"""
topological sorting:
                    this technique works only with DAG. travers the graph in such a order
                    that in every edges u->v , u comes before v in the ordering

application: package management, job scheduling.
where job A need to run 1st before job B.

Ans:
in this scenario we need to process the child node and then we will process the parent node.
in order to solve this problem we can use stack to store all child or child-child nodes in a stack
and once child processed we will put it into a visited list and pop its parent and so on.

time complexity = ?
space complexity = ?
"""

# A Python3 program to print topological sorting of a DAG
class topologicsort():
    def __init__(self):
        self.v = 6
        self.adj = [[] for z in range(self.v)]
        self.adj[5].append(2)
        self.adj[5].append(0)
        self.adj[4].append(0)
        self.adj[4].append(1)
        self.adj[2].append(3)
        self.adj[3].append(1)
        self.visited=[False for z in range(self.v)]
        self.stack = []
        self.topology = []
    def findchild(self):
        print("----")
        while self.stack.__len__() != 0:
            print(self.stack)
            parent = self.stack[-1]
            self.visited[parent]= True
            for i in self.adj[parent]:
                if self.visited[i] == False:
                    self.stack.append(i)
                    print("chield - {0}".format(self.stack))
            if parent == self.stack[-1]:
                self.topology.append(self.stack[-1])
                del self.stack[-1]

    def sort(self):
        for i in range(self.v):
            if self.visited[i] == False:
                self.stack.append(i)
                self.findchild()

obj = topologicsort()
print(obj.adj)
obj.sort()
print(obj.topology)
