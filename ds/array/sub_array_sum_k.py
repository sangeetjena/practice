"""
Given an array of integers nums and an integer k, return the total number of subarrays whose sum equals to k.

A subarray is a contiguous non-empty sequence of elements within an array.

Example 1:
Input: nums = [1,1,1], k = 2
Output: 2

Example 2:
Input: nums = [1,2,3], k = 3
Output: 2
"""
from collections import defaultdict


def sub_arr_sum_k(arr, k):
    dict = defaultdict(lambda: 0)
    cnt = 0
    sum = 0
    for elem in arr:
        sum = sum + elem
        if sum == k:
            cnt += 1
        if sum - k in dict:
            cnt += dict[sum - k]
        dict[sum] += 1
    return cnt


arr = [10, 2, -2, -20, 10]
print(sub_arr_sum_k(arr, -10))
