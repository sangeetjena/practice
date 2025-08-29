"""
https://leetcode.com/problems/subarray-sum-equals-k/description/

Given an array of integers nums and an integer k, return the total number of subarrays whose sum equals to k.

A subarray is a contiguous non-empty sequence of elements within an array.

 

Example 1:

Input: nums = [1,1,1], k = 2
Output: 2
Example 2:

Input: nums = [1,2,3], k = 3
Output: 2

Note: basic prefix sum problem.
#step 1:upfate count:  if total -k exiists in the dict then increament that value to count
#step 2: update to prefix sum: if total exists in dict then increment value by 1 else initiate value to 1

"""
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        prefix_sum = {0:1}
        total = 0 
        count = 0
        for num in nums:
            total +=  num
            #step 1:upfate count:  if total -k exiists in the dict then increament that value to count
            if total -k in prefix_sum.keys():
                count += prefix_sum[total-k]
            #step 2: update to prefix sum: if total exists in dict then increment value by 1 else initiate value to 1
            if total in prefix_sum.keys():
                prefix_sum[total] +=1
            else:
                prefix_sum[total] =1
        return count
