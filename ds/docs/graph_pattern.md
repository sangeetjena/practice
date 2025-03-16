
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
