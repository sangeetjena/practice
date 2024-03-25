"""
2035. Partition Array Into Two Arrays to Minimize Sum Difference
You are given an integer array nums of 2 * n integers.
You need to partition nums into two arrays of length n to minimize the absolute difference of the sums of the arrays.
To partition nums, put each element of nums into one of the two arrays.

Return the minimum possible absolute difference.

Hints: similar to meet at the middle
"""
from typing import List


def minimumDifference(nums: List[int]) -> int:
    # to handle negative case
    max_negative = min(nums)
    if max_negative<0:
        nums = [x + abs(max_negative) for x in nums]
    print(nums)
    sm = sum(nums)
    min_diff = 99999
    # this case is not valid for inputs like  [36,-36] hence can't take sum/2
    # if sm % 2 == 0:
    #     rng = int(sm / 2)
    # else:
    #     rng = int((sm + 1) / 2)
    rng = sm
    print(rng)
    dp = [[0 for x in range(0, (rng + 1))] for y in range(len(nums) + 1)]
    for x in range(len(nums)+1):
        dp[x][0] = 1
    for i in range(1, len(nums) + 1):
        for j in range(1, rng + 1):
            if nums[i-1] <= j:
                dp[i][j] = dp[i - 1][j] + dp[i - 1][j - nums[i-1]]
            else:
                dp[i][j] = dp[i - 1][j]
    for x in reversed(range(len(dp[-1]))):
        if dp[-1][x] == 0:
            continue
        else:
            if abs((sm - x) - x) < min_diff:
                min_diff = abs((sm - x) - x)
    print(dp)
    print("min diff = {} ".format(min_diff))
    return min_diff


nums = [36,-36]
nums = [76,8,45,20,74,84,28,1]
minimumDifference(nums)