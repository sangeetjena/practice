"""
There are n computers numbered from 0 to n-1 connected by ethernet cables connections forming a network where
connections[i] = [a, b] represents a connection between computers a and b.
 Any computer can reach any other computer directly or indirectly through the network.

Given an initial computer network connections.
You can extract certain cables between two directly connected computers,
and place them between any pair of disconnected computers to make them directly connected.
Return the minimum number of times you need to do this in order to make all the computers connected.
If it's not possible, return -1.

Input: n = 4, connections = [[0,1],[0,2],[1,2]]
Output: 1
Explanation: Remove cable between computer 1 and 2 and place between computers 1 and 3.
"""
visited = []
dfs = []
extra_edges = 0
cluster = 0


def find_edges_and_nodes(arr):
    global extra_edges
    edges = 0
    nodes = 0
    while len(dfs) > 0:
        node = dfs[-1]
        del dfs[-1]
        visited.append(node)
        nodes += 1
        for x in range(len(arr[node])):
            if arr[node][x] == 0 or x in visited:
                continue
            if x not in dfs:
                dfs.append(x)
            edges += 1
    if edges - (nodes - 1) < 0:
        return 0
    extra_edges = extra_edges + (edges - (nodes - 1))
    print(extra_edges, edges,nodes)


def no_of_opperation(arr):
    global dfs, visited, cluster
    for i in range(len(arr)):
        if i in visited:
            continue
        else:
            cluster += 1
            dfs.append(i)
            find_edges_and_nodes(arr)
    if extra_edges >= cluster - 1:
        return cluster - 1
    else:
        return -1


graph = [[0, 1, 1, 0],
         [1, 0, 1, 0],
         [1, 1, 0, 0],
         [0, 0, 0, 0]]
print(no_of_opperation(graph))
visited = []
dfs = []
extra_edges = 0
cluster = 0
graph = [[0, 1, 1, 0, 0, 0, 0],
         [1, 0, 1, 0, 0, 0, 0],
         [1, 1, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 1, 0],
         [0, 0, 0, 0, 1, 0, 1],
         [0, 0, 0, 0, 0, 1, 0]]
print(no_of_opperation(graph))
