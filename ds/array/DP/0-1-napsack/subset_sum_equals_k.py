"""
target sum = k

"""
def sub_set_sum_equals_to_k(arr, k):
    tmp_arr = [[0 for i in range(k +1)]  for x in range(len(arr) +1)]
    for i in range(len(tmp_arr)):
        tmp_arr[i][0] = 1
    for i in range(1, len(arr) + 1):
        for j in  range(1, k+1):
            if arr[i-1] > j:
                tmp_arr[i][j] = tmp_arr[i-1][j]
            else:
                tmp_arr[i][j] = tmp_arr[i-1][j] + tmp_arr[i-1][j-arr[i-1]]
    return tmp_arr

print(sub_set_sum_equals_to_k([3,2,3,5,4,5], 5))

print(sub_set_sum_equals_to_k([3,2,3,5,4,5], 10))
