"""
subset sum equals to k:
link: https://www.youtube.com/watch?v=hqGa65Rp5LQ&t=383s
"""
def sub_set_sum_equals_to_k(arr, sum):
    arr = sorted(arr, reverse=False)
    dp = [[0 for x in range(sum + 1)] for x in range(len(arr)+1)]
    for i in range(len(arr)):
        dp[i][0] = 1
    for i in range(1, len(arr)+1):
        for y in range(1, sum + 1):
            if arr[i-1] <= y:
                # 1st one - if not consider that element
                #2 - if consider the element, ed sum will reduce and elemnet also eleminated
                dp[i][y] = dp[i-1][y] + dp[i-1][y-arr[i-1]]
            else:
                dp[i][y] = dp[i-1][y]
    print(dp)
    return dp[-1][-1]

arr = [1,2,3,5,6,7]
# (7,3), (3,2,5), (6,3,1),(7,1,2)
print(sub_set_sum_equals_to_k(arr,10))

arr = [5,5]
print(sub_set_sum_equals_to_k(arr,10))

