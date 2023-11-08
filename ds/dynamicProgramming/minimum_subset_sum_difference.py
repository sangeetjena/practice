"""
find number of subset possible in an array whose difference is minimum.
"""
def subset_diff(arr, sum):
    dp = [[0 for x in range(sum+1)] for x in range(len(arr)+1)]
    dp[0][0] = 1
    for i in range(1, len(arr) + 1):
        for j in range(sum + 1):
            if j == 0:
                dp[i][j] = 1
                continue
            if arr[i-1] > j:
                dp[i][j] = dp[i-1][j]
            else:
                dp[i][j] = (dp[i-1][j] + dp[i-1][j - arr[i-1]])
    first = 0
    second = 0
    for i in reversed(range(sum+1)):
        if dp[-1][i] != 0:
            if(first == 0):
                first = i
                if(dp[-1][i] > 1):
                    second = i
                    break
            else:
                second = i
                break
    print(dp)
    return first - second

arr = [1,5,6,2,4]
print(subset_diff(arr, sum(arr)//2 + 1 ))

arr = [1,5,6,2,4,3]
print(subset_diff(arr, sum(arr)//2 + 1 ))


