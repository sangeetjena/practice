# in this approach child lookup parent node then decide which node to connect.
# here it start from 0,0 not and systematically keep looking to all its incremental neighbour
# Note: one problem of this approach is if we give random node ( mid point or top right corner then it will fail
# solution: djkstras or kruskas.
def min_cost_path_tabulisation(arr, memo):
    memo[0][0] = arr[0][0]
    for i in range(1, len(arr)):
        memo[0][i] = memo[0][i - 1] + memo[0][i]
    for i in range(1, len(arr)):
        memo[i][0] = memo[i-1][0] + arr[i][0]
    for i in range(1, len(arr)):
        for j in range(1, len(arr)):
            memo[i][j] = min(memo[i - 1][j], memo[i][j - 1], memo[i - 1][j - 1]) + arr[i][j]
    return memo[2][2]


cost = [[1, 2, 3],
        [4, 8, 2],
        [1, 5, 3]]
memo = [[0 for i in range(3)] for i in range(3)]
print(min_cost_path_tabulisation(cost, memo))
