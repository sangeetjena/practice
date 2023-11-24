"""
longest common palindromic subsequence: extension to LCS.
reverse the other string and apply LCS.
"""


def lcs_pallindrom(arr):
    dp = [[0 for x in range(len(arr) + 1)] for x in range(len(arr) + 1)]
    arr1 = "".join(reversed(arr))
    print(arr1)
    for i in range(1, len(arr) + 1):
        for j in range(1, len(arr1) + 1):
           if arr[i-1] == arr1[j-1]:
               dp[i][j] = 1 + dp[i-1][j-1]
           else:
               dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[-1][-1]

arr = "aaabca"
print(lcs_pallindrom(arr))
