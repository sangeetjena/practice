"""
https://leetcode.com/problems/subarray-product-less-than-k/description/
https://www.youtube.com/watch?v=Cg6_nF7YIks

Given an array of integers nums and an integer k, return the number of contiguous subarrays where the product of all the elements in the subarray is strictly less than k.

 

Example 1:

Input: nums = [10,5,2,6], k = 100
Output: 8
Explanation: The 8 subarrays that have product less than 100 are:
[10], [5], [2], [6], [10, 5], [5, 2], [2, 6], [5, 2, 6]
Note that [10, 5, 2] is not included as the product of 100 is not strictly less than k.
Example 2:

Input: nums = [1,2,3], k = 0
Output: 0
"""


class Solution:
    def numSubarrayProductLessThanK(self, nums: List[int], k: int) -> int:
        if k <= 1:
            return 0

        count = 0
        product = 1
        i, j = 0, 0

        while j < len(nums):
            product = product * nums[j]
            if product < k:
                # formula : the total window we will add that many subarray it will form.
                count = count + (j - i + 1)
            elif product >= k:
                while product >= k:
                    product = product // nums[i]
                    i = i + 1
                # formula: the total window we will add that many subarray it will form.
                count = count + (j - i + 1)
            j = j + 1

        return count
