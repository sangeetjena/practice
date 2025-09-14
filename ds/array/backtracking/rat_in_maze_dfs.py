"""
check if mouse can exit the mesh or not
"""
def RatInMazeDfs(arr, di, dj):
    stck = [(0, 0)]
    p = [0, 1, -1]
    q = [0, 1, -1]
    visitd = []
    while len(stck) > 0:
        x, y = stck[-1]
        del stck[-1]
        visitd.append((x, y))
        print(visitd)
        for a in p:
            for b in q:
                # (a != 0 and b != 0) - don't move diagonally
                # (x + a < 0 or x + a > len(arr) - 1 or y + b < 0 or y + b > len(arr) - 1) -- next point should be within metrix
                # arr[x + a][y + b] == 0 allowed to move in this position
                # (x + a, y + b) in visitd -- should not has visited
                if (a != 0 and b != 0) or (x + a < 0 or x + a > len(arr) - 1 or y + b < 0 or y + b > len(arr) - 1) or \
                        arr[x + a][y + b] == 0 or (x + a, y + b) in visitd:
                    continue
                if (x + a) == di and (y + b) == dj:
                    return True
                stck.append((x + a, y + b))
    return False


arr = [[1, 1, 1, 1],
       [1, 1, 0, 1],
       [0, 1, 1, 1],
       [1, 0, 1, 1]]
print(RatInMazeDfs(arr, 3, 3))
