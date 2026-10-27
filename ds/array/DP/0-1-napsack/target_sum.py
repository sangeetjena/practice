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
        # in one set one element will be there and in other set 0 element will be there.
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
class Solution:
    def dfs(self, currsm, i,target, nums):
        if i == len(nums):
            return 1 if currsm == target else 0
        if (i,currsm) in self.dp:
            return self.dp[(i,currsm)]
         # for each element i have only two option, either i will take it as +ve or -ve 
        self.dp[(i, currsm)] = (self.dfs(currsm + nums[i], i+1, target, nums) 
            + self.dfs(currsm - nums[i], i+1, target,  nums))
        return self.dp[(i, currsm)]

    def findTargetSumWays(self, nums: List[int], target: int) -> int:
        self.dp = defaultdict(int)
        return self.dfs(0,0,target, nums)
        


