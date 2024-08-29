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
