"""
https://leetcode.com/problems/count-number-of-nice-subarrays/description/

Given an array of integers nums and an integer k. A continuous subarray is called nice if there are k odd numbers on it.

Return the number of nice sub-arrays.

 

Example 1:

Input: nums = [1,1,2,1,1], k = 3
Output: 2
Explanation: The only sub-arrays with 3 odd numbers are [1,1,2,1] and [1,2,1,1].
Example 2:

Input: nums = [2,4,6], k = 1
Output: 0
Explanation: There are no odd numbers in the array.
Example 3:

Input: nums = [2,2,2,1,2,2,1,2,2,2], k = 2
Output: 16

 

Note: exactly same as prefix sum, only one catch is to convert all value in the array to o or 1
2- this also can be solved using sliding window.
"""

class Solution:
    def numberOfSubarrays(self, nums: List[int], k: int) -> int:
        # here only one thing matters is if a number is odd or not
        nums = [1 if num%2!=0 else 0 for num in nums]
        print(nums)
        total = 0
        count = 0
        prefix_sum = {0:1}
        for num in nums:
            total+=num
            if total -k in prefix_sum.keys():
                count+= prefix_sum[total-k]
            if total in prefix_sum.keys():
                prefix_sum[total] += 1
            else:
                prefix_sum[total] = 1
        return count
            
