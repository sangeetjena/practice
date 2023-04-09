"""DFS visits vertices as far as possible along each branch before backtracking.
It starts at the root node and explores as far as possible along each branch before backtracking.
DFS is best suited for traversing a graph where depth is more important than breadth.

DFS (Depth First Search) is a graph traversal algorithm that can be applied in various domains and has several applications, including:

1. Pathfinding and maze generation
2. Topological sorting
3. Graph and network analysis
4. Finding strongly connected components
5. Finding all the vertices reachable from a given source vertex
6. Solving puzzles (such as Sudoku)
7. Data compression
8. Model checking
9. Finding cycles in a graph.


Summary: stack implementation, pop from end and print it (lifo)
"""

class graph:
    def __init__(self, nodes):
        self.data = {}
        self.visited = []
        self.stack = []
        self.path = []

    def dfs(self, start):
        self.stack.append(start)
        while len(self.stack)>0:
            element = self.stack[-1]
            del self.stack[-1]
            self.visited.append(element)
            self.path.append(element)
            for i in self.data[element]:
                if i in self.visited:
                    continue
                self.visited.append(i) # as we are deleting the element from stack so we can add to visited as soon as we
                                        # add to stack. else we had to insert to visited after parsing.
                self.stack.append(i)
            print(self.stack)


graph = graph(5)
graph.data = {
    'A': set(['B', 'C']),
    'B': set(['D']),
    'C': set(['F']),
    'D': set(['E']),
    'E': set([]),
    'F': set(['E'])
}
graph.dfs('A')
print(graph.path)