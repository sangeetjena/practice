import sys
"""
application: minimum edges to connect to a city (MST)
in shortest path also we can apply this if -ve edges are there else djiskstras is better.
"""
class Graph:
    def __init__(self,v):
        self.v = v
        self.graph = [[0 for i in range(v)] for i in range(v)]
        self.visited = [False for i in range(v)]
        self.weight = [sys.maxsize for i in range(v)]
    def getminnode(self):
        # get min node from the weighted list
        minnode = 0
        min = sys.maxsize
        for i in range(self.v):
            if self.visited[i] == False and self.weight[i]<min:
                minnode = i
                min = self.weight[i]
        return minnode

    def primMST(self):
        print(self.weight)
        print(self.visited)

    def mst(self):
        self.weight[0] = 0
        for i in range(self.v):
            minnode = self.getminnode()
            self.visited[minnode] = True
            for i in range(self.v):
                if (self.graph[minnode][i] != 0 and self.visited[i] == False and self.graph[minnode][i]<self.weight[i]):
                    self.weight[i]=self.graph[minnode][i]

if __name__ == '__main__':
    g = Graph(5)
    g.graph = [[0, 2, 0, 6, 0],
               [2, 0, 3, 8, 5],
               [0, 3, 0, 0, 7],
               [6, 8, 0, 0, 9],
               [0, 5, 7, 9, 0]]
    print(g.graph)
    g.mst()
    g.primMST()