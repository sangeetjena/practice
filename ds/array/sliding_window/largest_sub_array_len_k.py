"""
https://leetcode.com/problems/largest-subarray-length-k/

An array A is larger than some array B if for the first index i where A[i] != B[i], A[i] > B[i].

For example, consider 0-indexing:

[1,3,2,4] > [1,2,2,4], since at index 1, 3 > 2.
[1,4,4,4] < [2,1,1,1], since at index 0, 1 < 2.
A subarray is a contiguous subsequence of the array.

Given an integer array nums of distinct integers, return the largest subarray of nums of length k.

 

Example 1:

Input: nums = [1,4,5,2,3], k = 3
Output: [5,2,3]
Explanation: The subarrays of size 3 are: [1,4,5], [4,5,2], and [5,2,3].
Of these, [5,2,3] is the largest.

Note: use sliding window of size 3 , convert arr to string/concatenate then convert it to an integer, capture the max int -> then at last convert int to array.
other way is bellow one.
"""
class Solution:
    def largestSubarray(self, nums: List[int], k: int) -> List[int]:
        prev = 0
        for i in range(1, len(nums)-k+1):
            if nums[i]> nums[prev]:
                prev = i
        return nums[prev:prev+k]


========
class Solution:
    def largestSubarray(self, nums: List[int], k: int) -> List[int]:
        mx = 0
        res = []
        for i in range(len(nums)-k+1):
            tmp = nums[i:i+k]
            if len(res) == 0:
                res = tmp
                continue
            for i in range(k):
                if res[i] > tmp[i]:
                    break
                if res[i] < tmp[i]:
                    res = tmp
                    break
        return res

        
