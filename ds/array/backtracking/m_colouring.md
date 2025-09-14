```

You are given an undirected graph consisting of V vertices and E edges represented by a list edges[][], along with an integer m. Your task is to determine whether it is possible to color the graph using at most m different colors such that no two adjacent vertices share the same color. Return true if the graph can be colored with at most m colors, otherwise return false.

Note: The graph is indexed with 0-based indexing.

Input: V = 4, edges[][] = [[0, 1], [1, 3], [2, 3], [3, 0], [0, 2]], m = 3
Output: true
Explanation: It is possible to color the given graph using 3 colors, for example, one of the possible ways vertices can be colored as follows:


```
<img width="257" height="225" alt="image" src="https://github.com/user-attachments/assets/95b415d1-fac7-441e-a522-33bad5881d85" />


``` python
def valid_col(arr, i):
    for y in range(len(arr)):
        if arr[i][y] == 0:
            continue
        if node_colour[i] == node_colour[y]:
            return False
    return True

def m_colouring(arr, i, node_colours):
    if i > len(arr)-1:
        return True
    print(i)
    for col in colours:
        node_colours[i] = col
        if valid_col(arr, i):
            if m_colouring(arr, i+1, node_colours):
                return True
        node_colours[i] = 0
    return False

#2 - white 3- red, 4- green
colours = [2, 3, 4 ]
node_colour = [0,0,0,0]
graph = [
        [0, 1, 1, 1],
        [1, 0, 1, 0],
        [1, 1, 0, 1],
        [1, 0, 1, 0],
    ]
m_colouring(graph, 0, node_colour)
print(node_colour)
```

