"""
312. Burst Balloons
https://leetcode.com/problems/burst-balloons/description/

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
        # Add 1 at both ends to handle edge balloons easily
        nums = [1] + nums + [1]

        n = len(nums)

        dp = [[0] * n for _ in range(n)]

        # length = size of the subarray (number of balloons to burst)
        for length in range(1, n - 1):
            # left = starting index of the current interval
            for left in range(1, n - length):
                right = left + length - 1  # right = ending index of interval

                # Now we try bursting each balloon 'k' last in this interval (left..right)
                for k in range(left, right + 1):
                    # dp[left][k-1] => coins from left side of k
                    # dp[k+1][right] => coins from right side of k
                    # nums[left-1]*nums[k]*nums[right+1] => coins from bursting k last
                    dp[left][right] = max(
                        dp[left][right],
                        dp[left][k - 1] + dp[k + 1][right] + nums[left - 1] * nums[k] * nums[right + 1]
                    )

        # The final answer is dp[1][n-2], which represents bursting all real balloons
        # (excluding the two artificial 1s at the ends)
        print(dp)
        return dp[1][n - 2]

