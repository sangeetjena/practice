"""
there is one basket containing oranges.
2- orten
1- normal
0 - no orange
if any roten orange is ther it can roten it adjacent orange. find no if it is possible to rotten all oranges at what time
if not return -1
"""
def rotten_orange(arr):
    print(arr)
    bfs_orange_stck = []
    time_cnt = 0
    stck_len = 0
    curr_len = 0
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            if arr[i][j] == 2:
                bfs_orange_stck.append((i,j))
    stck_len = len(bfs_orange_stck)
    while len(bfs_orange_stck)> 0:
        curr_pos = bfs_orange_stck[0]
        move = [0,1,-1]
        del bfs_orange_stck[0]
        curr_len +=1
        if curr_len == stck_len:
            curr_len = 0
            stck_len = len(bfs_orange_stck)
            time_cnt +=1
        for i in move:
            for j in move:
                if (i!= 0 and j != 0) or \
                        i==j or curr_pos[0]+i >len(arr)-1 or\
                        curr_pos[1]+j >len(arr)-1 or \
                        curr_pos[0] + i < 0 or \
                        curr_pos[1] + j < 0 or\
                        arr[curr_pos[0]+i][curr_pos[1]+j] in [0,2]:
                    continue
                bfs_orange_stck.append((curr_pos[0] +i, curr_pos[1]+j))
                arr[curr_pos[0] + i][curr_pos[1] + j] = 2
    print(arr)
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            if arr[i][j] == 1:
                return -1
    return time_cnt

arr=[[2,1,0,1],
     [0,2,0,2],
     [1,1,0,1]]
print(rotten_orange(arr))