def find_partitions(arr):
    set = [[0 for i in range(len(arr) + 1)] for i in range(len(arr) + 1)]
    for i in range(1, len(arr) + 1):
        for j in  range(1, i+1):
            if j==1 or j==i:
                set[i][j] = 1
            else:
                set[i][j] = j * set[i-1][j] + set[i-1][j-1]
    return set

print(find_partitions([1,2,3, 4])[4][3])