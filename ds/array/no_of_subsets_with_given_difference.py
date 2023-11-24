"""
no of subsets with given difference = k
ex: similar to subset sum = k
s1 + s2 = s
s1 - s2 = d
s1 = (s + d) /2
we need to find how many set we can form whose sum = s1
"""


def find_subset_sum_k(arr, diff):
    s = sum(arr)
    if((s-diff)%2 != 0):
        return 0
    sum1 = int((s - diff)/2)
    dp = [[0 for x in range(sum1 + 1)] for x in range(len(arr) + 1)]
    for i in range(len(arr) + 1):
        dp[i][0] = 1
    for i in range(1, len(arr) + 1):
        for j in range(1, sum1 + 1):
            if arr[i - 1] > j:
                dp[i][j] = dp[i - 1][j]
            else:
                dp[i][j] = dp[i - 1][j] + dp[i - 1][j - arr[i - 1]]
    return dp[-1][-1]


diff = 3
arr = [1,2,3,5,6,7]
print(find_subset_sum_k(arr, diff))
