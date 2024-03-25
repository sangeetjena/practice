"""
detect cycle in a directed graph.
"""

def detect_cycle(adjc_list, node):
    dfs = []
    visited = [0 for x in range(0, len(adjc_list))]
    traversed = [0 for x in range(0, len(adjc_list))]
    visited[node] = 1
    dfs.append(node)
    while len(dfs) > 0:
        node = dfs[-1]
        if traversed[node] == 1:
            del dfs[-1]
            # when i am not advancing and traversing back then set visited = 0
            visited[node] = 0
            continue
        for i in adjc_list[node]:
            if visited[i] == 1:
                return "detect cycle"
            if traversed[i] != 1:
                dfs.append(i)
        visited[node] = 1
        traversed[node] = 1
    return "no cycle"

def find_cycle_in_graph(adjc_list):
    for i in range(len(adjc_list)):
        detectCycle = detect_cycle(adjc_list, i)
        if detectCycle == "detect cycle":
            print(" cycle detected at nor {}".format(i))
            return


adjc_list = [[],[]]