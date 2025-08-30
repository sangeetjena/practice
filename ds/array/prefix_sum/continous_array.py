"""
https://leetcode.com/problems/contiguous-array/description/

Given a binary array nums, return the maximum length of a contiguous subarray with an equal number of 0 and 1.

 

Example 1:

Input: nums = [0,1]
Output: 2
Explanation: [0, 1] is the longest contiguous subarray with an equal number of 0 and 1.
Example 2:

Input: nums = [0,1,0]
Output: 2
Explanation: [0, 1] (or [1, 0]) is a longest contiguous subarray with equal number of 0 and 1.
Example 3:

Input: nums = [0,1,1,1,1,1,0,0,0]
Output: 6
Explanation: [1,1,1,0,0,0] is the longest contiguous subarray with equal number of 0 and 1.

Note: prefix sum problem but instee of searching storing the count, store the position of the index and capture max len at each iteration.

"""

class Solution:
    def findMaxLength(self, nums: List[int]) -> int:
        nums = [1 if i == 1  else -1 for i in nums]
        prefixsum = {0:-1}
        total_sum = 0
        max_len = 0
        for i in range(len(nums)):
            total_sum+=nums[i]
            if total_sum in prefixsum.keys() :
                max_len = max(max_len, i-prefixsum[total_sum])
            else:
                prefixsum[total_sum] = i
        return max_len


            



            
