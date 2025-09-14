def is_safe(arr, x,y):
    #check vertically
    x1 = x
    while x1>=0:
        if not (x1 == x):
            if arr[x1][y] == 1:
                return False
        x1-=1
    # check upper right diagonally
    x1 = x
    y1 = y
    while x1 >= 0 and y1 < len(arr):
        if not (x1 == x and y1 == y):
            if arr[x1][y1] == 1:
                return False
        x1-=1
        y1+=1
    #check upper left diagonal
    x1 = x
    y1 = y
    while x1 >= 0 and y1 >0:
        if not (x1 == x and y1 == y):
            if arr[x1][y1] == 1:
                return False
        x1 -= 1
        y1 -= 1
    return True

def place_n_queen(arr, x):
    if x > len(arr)-1:
        return True
    for i in range(0, len(arr)):
        arr[x][i] = 1
        if not is_safe(arr, x, i):
            arr[x][i] = 0
            continue
        if place_n_queen(arr, x+1):
            return True
        arr[x][i] = 0

board = [[0,0,0,0],
        [0,0,0,0],
         [0,0,0,0],
         [0,0,0,0]]

print(place_n_queen(board,0))
print(board)
