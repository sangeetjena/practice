"""
Adjacent Increasing Subarrays Detection I
https://leetcode.com/problems/adjacent-increasing-subarrays-detection-i/description/

Given an array nums of n integers and an integer k, determine whether there exist two adjacent subarrays of length k such that both subarrays are strictly increasing.
Specifically, check if there are two subarrays starting at indices a and b (a < b), where:

Both subarrays nums[a..a + k - 1] and nums[b..b + k - 1] are strictly increasing.
The subarrays must be adjacent, meaning b = a + k.
Return true if it is possible to find two such subarrays, and false otherwise.

 

Example 1:

Input: nums = [2,5,7,8,9,2,3,4,3,1], k = 3

Output: true

Explanation:

The subarray starting at index 2 is [7, 8, 9], which is strictly increasing.
The subarray starting at index 5 is [2, 3, 4], which is also strictly increasing.
These two subarrays are adjacent, so the result is true.
Example 2:

Input: nums = [1,2,3,4,4,4,4,5,6,7], k = 5

Output: false

Note:
take prev and curr, keep increasing curr length untill find a breaking point where eleement is not strictly increasing.
at each breaking point store curr to prev and make crr=1 and check if prev==curr==k or curr >=2*k

"""

class Solution:
    def hasIncreasingSubarrays(self, nums: List[int], k: int) -> bool:
        prev, curr = 1,1
        if len(nums)<k:
            return False
        for i in range(0, len(nums)-1):
            if nums[i+1]> nums[i]:
                curr+=1
            else:
                if curr>=2*k or (prev>=k and curr >=k):
                    return True
                prev = curr
                curr = 1
        print(curr)
        if curr>=2*k or (prev>=k and curr >=k):
                    return True
        return False 
        
