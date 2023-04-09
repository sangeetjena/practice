"""
Breath first search( bfs) :
this is a searching technique, where the search start at root of the graph and traverse all nodes in the current
depth, before moving to the next depth.

BFS (Breadth First Search) is a graph traversal algorithm that can be applied in various domains and has several applications, including:

1. Shortest path finding
2. Network traversal (web crawling)
3. Peer-to-peer networking
4. Social Network Analysis
5. Solving puzzles (such as Rubik's Cube)
6. Checking if a graph is bipartite
7. Broadcasting in Network
8. Garbage collection in computer systems
9. Model checking and formal verification
10. Finding all connected components in an undirected graph.

Summary: queue implementation, pull start  from end and print it (fifo)
"""
class Graph:
    def __init__(self,nodes):
        self.graph = [[] for i in range(nodes)]
        self.visited = [False for i in range(nodes)]
        self.queue = []
        self.bst = []
    def addEdge(self, u, v):
        self.graph[u].append(v)

    def bfs(self, start):
        self.queue.append(start)
        self.visited[start] = True
        while (len(self.queue) != 0):
            element = self.queue[0]
            self.bst.append(element)
            del self.queue[0]
            for x in self.graph[element]:
                if self.visited[x] == False:
                    self.visited[x] = True
                    self.queue.append(x)




g = Graph(4)
g.addEdge(0, 1)
g.addEdge(0, 2)
g.addEdge(1, 2)
g.addEdge(2, 0)
g.addEdge(2, 3)
g.addEdge(3, 3)
g.bfs(0)
print(g.bst)