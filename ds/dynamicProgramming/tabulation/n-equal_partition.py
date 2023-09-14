"""
variation of bounded subset sum.
   0,1,2,3,4,5,6,7,8,9,10,11
0 [0,0,0,0,0,0,0,0,0,0,0,0]
1 [0]
2 [0]
3 [0]
4 [0]
5 [0]
"""
def find_n_equal_partiton(arr, n):
    k = int(sum(arr)/n)
    if sum(arr)%n != 0:
        return False
    dp = [[0 for x in range(k+1)] for x in range(len(arr)+1)]
    print(k)
    for i in range(1,len(dp)+1):
        for j in range(k+1):
            if arr[i-1] >= j:
                dp[i][j]= dp[i-1][j]
            else:
                dp[i][j] = 1 + dp[i-1][j-arr[i-1]]

    return dp

print(find_n_equal_partiton([3,2,5,6,8],2))