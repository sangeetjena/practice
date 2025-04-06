
## Pattern #1 - Problems Involving Shortest Path Algorithm in Unweighted Graphs
```
Algorithms Used: Breadth First Search

These are the problems where you need to directly or indirectly compute the shortest distance to the nodes.
These could be via a single source or multiple sources.



For example: let us take a look at the Rotting Oranges Problem on Leetcode.
The key idea to solve this problem is to determine that the time at which each orange becomes rotten is equal to the shortest distance of that orange from its nearest rotten orange.
This can be easily solved by using Breadth First Search and making sure that when we perform a breadth-first search,
we add the coordinates of the rotten oranges in the queue.
```
## Pattern #2 - Problems Where We Start Graph Traversal from Cells on Boundaries
```
These are the problems where we need to start the graph traversal from the boundaries of the cells,
for ex take a look at the Pacific Atlantic Problem. In this problem,
if you start BFS from every cell and try to see if you can reach either the Pacific or Atlantic Ocean,
the solution’s time complexity would increase.
This is because you would have to start the BFS O(MxN) times and each BFS can take up to O(MN) time as well.
So, overall complexity becomes O(M*N) ^2). So, instead of that, we do the BFS only starting from the boundary cells,
therefore we reduce the complexity to O (M*N*(M + N)).

Algorithms Used: Breadth First Search and Depth First Search

```
## Pattern #3 - Problems Where We Model Input as a Graph and then use topological sorting to get the output.
```
These are the problems where we need to first model the input given in the problem as a graph and then either detect there is a cycle or determine the order using topological sort and use this information.



For example: In the Alien Dictionary problem on Leetcode we are given a new language where the lexicographic order of the letters is not known. However, we are given the list of some sample words in lexicographic order is given. Using that we need to determine the valid order of letters in this new “alien” language. For ex, if the input is ["wrt","wrf","er","ett","rftt"] then using it we can determine that the order of letters in this alien language is [“w”, “e”, “r”, “t”, “f”].



We can solve this problem first by modeling each letter as a node and then we determine which letter comes before which letter using consecutive words. For ex, if we compare “wrt” and “wrf” we can determine that “t” should come before “f”. So, we add an edge from “t” to “f”. Similarly, when we compare “wrf” to “er” we can determine that “w” should come before “e”. So, we add an edge from “w” to “e” in the graph. Like this we add all the edges and then topological sort the graph.



Another example of this problem is Course Schedule where we model each course as a node.



Topological Sorting and Cycle Detection
```


## Pattern #4 - Problems Involving Shortest Path Algorithm Over Weighted Graphs/Binary Weighted Graphs
```
These are the problems that can directly be solved by applying the standard shortest path algorithm after modeling the input as a graph. For example, if we look at the Network Delay Time problems on Leetcode, the time it takes for the signal to reach the farthest node is the distance of the farthest node from the source node.



Another example can be Snakes & Ladder Problems on Leetcode. In this problem, we model each number within the snakes and ladder board as a node and model each dice roll as an edge with weight 1 (as we need to throw the dice once to follow this edge). Each snake or ladder can be modeled as an edge with weight 0 (as we don’t need to throw the dice to go over the edge).



Dijkstra’s algorithm and 0-1 BFS

```

## Pattern #5 - Problems Involving Minimum Spanning Tree
```
These are the problems that can directly be by applying either Kruskal’s or Prim’s algorithm. For example, Min Cost to Connect All Points For ex, in this problem, we model each point as a graph and model the edges b/w each node with the weight as the Manhattan distance b/w the two points. Then we apply any of the minimum spanning tree algorithms directly.
```


# Trie pattern

| LeetCode Link | Git Link |
|--------------|---------|
| [Search system](https://leetcode.com/problems/search-suggestions-system/description/?envType=problem-list-v2&envId=trie) | [Git Link](https://github.com/sangeetjena/practice/blob/master/ds/graph/trie/search.py) |
