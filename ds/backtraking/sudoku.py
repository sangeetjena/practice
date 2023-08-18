def check_valid(arr, element, i, j):
    #check row conflict
    for x in range(0,9):
        if x == j:
            continue
        if arr[i][x] == arr[i][j]:
            return False

    #check upper column
    for x in range(0,i):
        if x == i:
            continue
        if arr[x][j] == arr[i][j]:
            return False
    # check grid
    gi = 0 if i in [0,1,2] else 3 if i in [3,4,5] else 6
    gj = 0 if j in [0,1,2] else 3 if j in [3,4,5] else 6
    for x in range(gi, gi+3):
        for y in range(gj, gj+3):
            if x == i and y ==j:
                continue
            if arr[x][y] == arr[i][j]:
                return False
    return True

def sudoku(arr):
    for i in range(9):
        for j in range(9):
            if arr[i][j] != 0:
                continue
            for k in range(1,10):
                arr[i][j] = k
                if check_valid(arr, k, i,j ):
                    print("print {0}, {1}, {2}".format(i, j, arr[i][j]))
                    print(arr)
                    if sudoku(arr):
                        return True
                arr[i][j] = 0
            return False
    return True


sudoku_board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

sudoku(sudoku_board)
print(sudoku_board)
