import sys
def min_cost_path(arr, i, j):
    if i ==0 and j==0:
        return arr[0][0]
    if i<0 or i>len(arr)-1 or j<0 or j>len(arr)-1:
        return sys.maxsize
    return arr[i][j] + min(min_cost_path(arr, i-1,j),
                           min_cost_path(arr,i, j-1),
                           min_cost_path(arr, i-1, j-1))

cost = [[1, 2, 3],
        [4, 8, 2],
        [1, 5, 3]]
print(min_cost_path(cost,2,2))
