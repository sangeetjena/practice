def valid_move(arr, px,py, ln, visited):
    if px <0 or px > ln or py<0 or py>ln:
        return False
    if (px, py) in visited:
        return False
    if arr[px][py] == 0:
        return False
    return True
def find_rat_in_maze(arr, p_x, p_y, d_x, d_y, n, visited):
    moves = [0,1,-1]
    if (p_x, p_y) == (d_x, d_y):
        return True
    for i in moves:
        for j in moves:
            if (i==0 or j==0) and valid_move(arr, p_x + i,p_y+j,n, visited ):
                visited.append((p_x + i, p_y +j))
                if find_rat_in_maze(arr, p_x + i, p_y +j, d_x, d_y, n, visited):
                    return True
    return False


arr = [[1, 0, 0, 0],
       [0, 1, 0, 1],
       [0, 1, 0, 0],
       [1, 1, 1, 1]]
print(find_rat_in_maze(arr, 0, 0, 3, 3, 3, []))
