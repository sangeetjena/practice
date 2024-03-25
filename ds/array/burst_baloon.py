"""
Note: be carefull while using right index, it might go index out of range.
"""
def burst_baloon(arr):
    arr = [1] + arr + [1]
    dp = [[0 for i in range(len(arr))] for x in range(len(arr))]
    for window in range(1, len(arr) - 1):
        for i in range(1, len(arr) - window):
            left = i
            right = i + window - 1
            # print("dp left right")
            # print(left, right, window)
            for j in range(left, right +1):
                # print(j)
                dp[left][right] = max(dp[left][right],
                                      arr[j] * arr[left - 1] * arr[right + 1] +
                                      dp[left][j - 1] +
                                      dp[j + 1][right])
            #     print(arr[j] , arr[left - 1] , arr[right + 1] )
            #     print(dp[left][j - 1], dp[j + 1][right])
            # print(dp)
    print(dp[1][-2])
    return dp


arr = [1, 2, 3, 4]
print(burst_baloon(arr))
