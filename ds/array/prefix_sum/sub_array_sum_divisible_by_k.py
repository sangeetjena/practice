"""
https://leetcode.com/problems/subarray-sums-divisible-by-k/description/

Given an integer array nums and an integer k, return the number of non-empty subarrays that have a sum divisible by k.

A subarray is a contiguous part of an array.

 

Example 1:

Input: nums = [4,5,0,-2,-3,1], k = 5
Output: 7
Explanation: There are 7 subarrays with a sum divisible by k = 5:
[4, 5, 0, -2, -3, 1], [5], [5, 0], [5, 0, -2, -3], [0], [0, -2, -3], [-2, -3]
Example 2:

Input: nums = [5], k = 9
Output: 0


Note: same as prefix sum but insteed of substracting k value take mod value.
mod will give reminder, that means removing all the value divisible by k remain value (starting point of all divisible value)

"""
class Solution:
    def subarraysDivByK(self, nums: List[int], k: int) -> int:
        total = 0 
        prefix_sum = {0:1}
        prefix_sum[0] = 1
        count = 0
        for i in range(len(nums)):
            total += nums[i]
            mod = total % k
            if mod in prefix_sum:
                count+=prefix_sum[mod]
                prefix_sum[mod]+=1
            else:
                prefix_sum[mod] = 1
        return count
            

        
