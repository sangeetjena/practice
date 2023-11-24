def rat_in_maze_max_path(arr, i, j):
  if arr[i][j] == 1 or i<0 or i > len(arr) or j <0 or j > len(arr):
    return 0
  if i == 0 and j == 0:
    return 1
  max_path = max( rat_in_maze_max_path(arr,i-1,j), rat_in_maze_max_path(arr, i,j-1))
  if max_path > 0:
    return 1 + max_path
  return max_path

arr = [[0,0,0,0],
  [0,1,0,1],
  [0,0,0,0]]

print(rat_in_maze_max_path(arr,2,2))