```
https://leetcode.com/discuss/study-guide/3900838/%22Mastering-Graph-Algorithms%3A-A-Comprehensive-DSA-Graph-Common-Question-Patterns-CheatSheet%22
```
```
https://medium.com/@ninads79shukla/patterns-and-templates-for-common-data-structures-and-algorithm-questions-part-2-graphs-4398c6d0503c
```
```
https://hackernoon.com/5-graph-patterns-to-ace-coding-interviews
```
| Algorithm         | Purpose                                         | Graph Type                 | Edge Weights         | Key Characteristics                                   |
|-------------------|-------------------------------------------------|----------------------------|-----------------------|------------------------------------------------------|
| **Dijkstra's**     | Shortest path from a single source to all vertices | Weighted, directed/undirected | Non-negative         | Greedy algorithm; uses a priority queue; does not handle negative weights; not suitable for negative cycles. |
| **Prim's**        | Minimum Spanning Tree (MST)                     | Weighted, undirected       | Any (including zero) | Greedy algorithm; starts from an arbitrary node; expands the MST by adding the smallest edge connecting to a vertex outside the tree. |
| **Bellman-Ford**  | Shortest path from a single source to all vertices | Weighted, directed/undirected | Can be negative      | Dynamic programming approach; handles negative weights; can detect negative cycles; slower than Dijkstra's for large graphs. |
| **Kruskal's**     | Minimum Spanning Tree (MST)                     | Weighted, undirected       | Any (including zero) | Greedy algorithm; sorts edges by weight; uses Union-Find to prevent cycles; works well for sparse graphs. |

