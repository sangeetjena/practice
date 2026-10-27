"""
https://leetcode.com/problems/partition-equal-subset-sum/description/

Given an integer array nums, return true if you can partition the array into two subsets such that the sum of the elements in both subsets is equal or false otherwise.

Example 1:

Input: nums = [1,5,11,5]
Output: true
Explanation: The array can be partitioned as [1, 5, 5] and [11].
Example 2:

Input: nums = [1,2,3,5]
Output: false
Explanation: The array cannot be partitioned into equal sum subsets.
"""
class Solution:
    def canPartition(self, nums: List[int]) -> bool:
        sm = sum(nums)
        if sm%2!=0:
            return False
        md = sm//2
        dp = [[0 for x in range(md+1)] for y in range(len(nums)+1)]
        dp[0][0]=1
        # alter i, j position sequence that of dp
        for i in range(1,len(nums)+1):
            for j in range(0, md+1):
                if j == 0:
                    dp[i][j]=1
                    continue
                # id element i.e nums[i-1] value less than sum value ie j then reduce one element and reduce sum value also
                if nums[i-1] <= j:
                    dp[i][j] = dp[i-1][j]+ dp[i-1][j-nums[i-1]]
                else:
                # if element is greater than sum value then we can't consider that element and only option left is without taking that elemen if sum can form using previous element.
                    dp[i][j] = dp[i-1][j]
        return dp[-1][-1]>0

# memoisation 

class Solution:
    def dfs(self, currsm,target, i, nums):
        if i == len(nums):
            return 1 if currsm == target else 0
        if (i,currsm) in self.dp:
            return self.dp[(i, currsm)]
        # similar to target sum either i will take or not take .
        # there is another way to look at it , in one add value in other substract value and in this case target we have to take as 0
        self.dp[(i,currsm)] = self.dfs(currsm + nums[i], target,i+1, nums) + self.dfs(currsm, target, i+1, nums)
        return self.dp[(i,currsm)]

    def canPartition(self, nums: list[int]) -> bool:
        self.dp =  defaultdict(int)
        sm = sum(nums)
        if sm %2 !=0:
            return False
        target = sm // 2
        res = self.dfs(0, target, 0 ,nums)
        return True if res>0 else False
