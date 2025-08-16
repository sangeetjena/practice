"""
312. Burst Balloons
Solved
Hard
Topics
conpanies icon
Companies
You are given n balloons, indexed from 0 to n - 1. Each balloon is painted with a number on it represented by an array nums. You are asked to burst all the balloons.

If you burst the ith balloon, you will get nums[i - 1] * nums[i] * nums[i + 1] coins. If i - 1 or i + 1 goes out of bounds of the array, then treat it as if there is a balloon with a 1 painted on it.

Return the maximum coins you can collect by bursting the balloons wisely.

 

Example 1:

Input: nums = [3,1,5,8]
Output: 167
Explanation:
nums = [3,1,5,8] --> [3,5,8] --> [3,8] --> [8] --> []
coins =  3*1*5    +   3*5*8   +  1*3*8  + 1*8*1 = 167
Example 2:

Input: nums = [1,5]
Output: 10

"""
class Solution:
    def maxCoins(self, nums: List[int]) -> int:
        n=len(nums)
        nums.insert(0,1)
        nums.append(1)
        dp=[[0 for j in range(n+2)] for j in range(n+2)]
        for i in range(n,0,-1):
            for j in range(1,n+1):
                if i>j:
                    continue
                maxi=-maxsize
                for k in range(i,j+1):
                    coins=nums[i-1]*nums[k]*nums[j+1]+dp[i][k-1]+dp[k+1][j]
                    maxi=max(maxi,coins)
                dp[i][j]=maxi
        return dp[1][n]


arr = [1, 2, 3, 4]
print(burst_baloon(arr))
