"""
https://leetcode.com/problems/target-sum/
You are given an integer array nums and an integer target.

You want to build an expression out of nums by adding one of the symbols '+' and '-' before each integer in nums and then concatenate all the integers.

For example, if nums = [2, 1], you can add a '+' before 2 and a '-' before 1 and concatenate them to build the expression "+2-1".
Return the number of different expressions that you can build, which evaluates to target.

 

Example 1:

Input: nums = [1,1,1,1,1], target = 3
Output: 5
Explanation: There are 5 ways to assign symbols to make the sum of nums be target 3.
-1 + 1 + 1 + 1 + 1 = 3
+1 - 1 + 1 + 1 + 1 = 3
+1 + 1 - 1 + 1 + 1 = 3
+1 + 1 + 1 - 1 + 1 = 3
+1 + 1 + 1 + 1 - 1 = 3


Note: it is similar to subset sum = k, we need to devide nums to two sets one +ve and one -ve.
sum1 - sum2 = target # sum2 of -ve nos
sum1 - (totalsum -sum1) = target
2sum1 - totalum = target
sum1 = (target + totalsum) /2
now the problem became subset sum equals to sum1
"""
class Solution:
    def findTargetSumWays(self, nums: List[int], target: int) -> int:
        total = sum(nums)
        # if i have only one element and that one element match to target then there is only one way i canform the target
        if len(nums) == 1:
            return 1 if (nums[0] == target) or (-nums[0] == target) else 0
        if (total+target)%2 != 0:
            return 0
        # if i have all +ve no and sum is  < target value then we can't build partition in any way.
        if abs(target)> total:
            return 0
        sm1 = (total+target)//2
        
        dp = [[0 for i in range(sm1+1)] for j in range(len(nums)+1)]
        dp[0][0]=1
        for i in range(1,len(nums)+1):
            for j in range(sm1+1):
                if nums[i-1] <= j:
                    dp[i][j]= dp[i-1][j] + dp[i-1][j-nums[i-1]]
                else:
                    dp[i][j] = dp[i-1][j]
        print(dp)
        return dp[-1][-1]

# Memoisation:
=============
def find_target_sum_ways(arr, T):
    total = sum(arr)

    # If the target can't be generated using the given numbers
    if total < abs(T):
        return 0
    
    # Initialize a lookup table
    dp = [[-1 for _ in range(2*total+1)] for _ in range(len(arr))]
    
    return find_target_sum_ways_rec(arr, 0, T, dp)

def find_target_sum_ways_rec(arr, i, T, dp):
    # If all integers are processed
    if i == len(arr):
        # If target is reached
        if T == 0:
            return 1
        # If target is not reached
        return 0

    #If we have solved it earlier, then return the result from memory
    if dp[i][T] != -1:
        return dp[i][T]
    
    # Calculate both sub-problems and save the results in the memory
    dp[i][T] = find_target_sum_ways_rec(arr, i + 1, T + arr[i], dp) + \
               find_target_sum_ways_rec(arr, i + 1, T - arr[i], dp)
    
    return dp[i][T]


