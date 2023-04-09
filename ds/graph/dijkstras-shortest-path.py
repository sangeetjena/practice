"""
this is shortest path algorithm.
we will have a visited list and weight list.
weight list will contain minimum weight to connect indexed node.
we will always pick a node from wight list whose weight is minimum and not visited.
at the end of this process we will get shorted path to connect nodes.

this will work for path which has +ve weight.

application:
    optimisation, sortest path

time complexity : O(v2)
space complecity : ?
"""
import sys
class dijkstras():

    def __init__(self, graph,vertices):
        self.weightedVertices = [sys.maxsize]*vertices
        self.visitedSet = [False]*vertices
        self.vertices = vertices
        self.graph = graph

    def findMinimumNode(self):
        min = sys.maxsize
        minnode = 0
        for i in range(0,len(self.weightedVertices)):
            if self.weightedVertices[i]<min and self.visitedSet[i] != True:
                min = self.weightedVertices[i]
                minnode = i
        return minnode

    def shortestPath(self):
        self.weightedVertices[0] = 0
        for i in range(0,self.vertices):
            node = self.findMinimumNode()
            print("minimum node = {0}".format(node))
            self.visitedSet[node] = True
            for y in range(0,self.vertices):
                checknode = self.graph[node][y]
                if checknode!=0 and checknode not in self.visitedSet and self.weightedVertices[y]> checknode + self.weightedVertices[node]:
                    self.weightedVertices[y] = checknode + self.weightedVertices[node]
        print(self.weightedVertices)

if __name__ == "__main__":
    graph = [[0, 4, 0, 0, 0, 0, 0, 8, 0],
               [4, 0, 8, 0, 0, 0, 0, 11, 0],
               [0, 8, 0, 7, 0, 4, 0, 0, 2],
               [0, 0, 7, 0, 9, 14, 0, 0, 0],
               [0, 0, 0, 9, 0, 10, 0, 0, 0],
               [0, 0, 4, 14, 10, 0, 2, 0, 0],
               [0, 0, 0, 0, 0, 2, 0, 1, 6],
               [8, 11, 0, 0, 0, 0, 1, 0, 7],
               [0, 0, 2, 0, 0, 0, 6, 7, 0]
               ]
    g = dijkstras(graph, 9)
    g.shortestPath()