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
