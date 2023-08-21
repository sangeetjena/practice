import sys
def min_cost_path_memo(arr, i, j, memo):
    if i == j and j ==0:
        return arr[0][0]
    if i< 0 or j<0:
        return sys.maxsize
    if memo[i][j] != -1:
        return memo[i][j]
    # difference between recursion is it is storing value into an array. then when same point came again it will simply
    # return the value instead of recomputing again.
    memo[i][j]  = arr[i][j] + min(min_cost_path_memo(arr, i-1, j, memo),
                                  min_cost_path_memo(arr, i, j-1, memo),
                                  min_cost_path_memo(arr,i-1, j-1, memo))
    return memo[i][j]

cost = [[1, 2, 3],
        [4, 8, 2],
        [1, 5, 3]]

memo = [[-1 for i in range(3)] for i in range(3)]

print(min_cost_path_memo(cost,2,2,memo))