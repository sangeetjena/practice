def subset_sum(arr, i, target, dp):
    if target == 0:
        return 1
    if target <0 or i> len(arr)-1:
        return 0
    if dp[i][target] != -1:
        return dp[i][target]
    dp[i][target] = subset_sum(arr, i+1, target-arr[i], dp) + subset_sum(arr, i+1, target, dp)
    return dp[i][target]

arr = [1,2,1]
target = 2
dp = [[-1 for i in range(target+1)] for x in range(len(arr))]
print(subset_sum(arr,0,target,dp))

arr = [1,5,6,3,4]
target = 9
dp = [[-1 for i in range(target+1)] for x in range(len(arr))]
print(subset_sum(arr,0,target,dp))