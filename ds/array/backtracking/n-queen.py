import copy

def chack_fighing_queen(refboard, x, y):
    temp_ref = copy.deepcopy(refboard)
    lenqueen = len(refboard)
    if refboard[x][y] == 1 or refboard[x][y] == 2:
        return refboard
    else:
        temp_ref[x][y] = 1
    for i in range(0,len(refboard)):
        if (y+i) < lenqueen and temp_ref[x][y+i] != 1:
            temp_ref[x][y+i] = 2
        if y > i and temp_ref[x][y - i] != 1:
            temp_ref[x][y - i] = 2
        if (x + i) < lenqueen and temp_ref[x + i][y] != 1:
            temp_ref[x + i][y] = 2
        if x > i and temp_ref[x - 1][y] != 1:
            temp_ref[x - 1][y] = 2
        if x > i and y > i and temp_ref[x - i][y - i] != 1:
            temp_ref[x - i][y - i] = 2
        if (y + i) < lenqueen and (x + i) < lenqueen and temp_ref[x + i][y + i] != 1:
            temp_ref[x + i][y + i] = 2
    print(temp_ref)
    return temp_ref

def place_n_queen():
    nqueen_place = []
    level = 0
    parssedlevels = [[] for x in board]
    levelzero = 0
    while len(nqueen_place) != len(board):
        print(level)
        print(nqueen_place)
        if level == 0 and levelzero < len(board):
            ret = chack_fighing_queen(board, 0, levelzero)
            if ret != board:
                nqueen_place.append(ret)
                level+=1
                levelzero+=1
            else:
                levelzero+=1
                continue
        else:
            prevlevel = level
            for i in range(0, len(board)):
                print("i value - " + str(i), prevlevel, level)
                if (i in parssedlevels[level]):
                    continue
                ret = chack_fighing_queen(nqueen_place[level-1], level, i)
                parssedlevels[level].append(i)
                if ret != nqueen_place[level - 1]:
                    nqueen_place.append(ret)
                    level += 1
                    print("enter break")
                    print(prevlevel, level)
                    break
            if prevlevel == level:
                parssedlevels[level] = []
                level -=1
                del nqueen_place[-1]
        if level == 0 and levelzero >= len(board):
            print(" no position found")
            break
    print(nqueen_place)





board = [[0,0,0,0],
        [0,0,0,0],
         [0,0,0,0],
         [0,0,0,0]]
refboard = board
place_n_queen()
