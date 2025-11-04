"""
similar to adjacent increasing subarray 1
https://leetcode.com/problems/adjacent-increasing-subarrays-detection-ii/description/?envType=company&envId=google&favoriteSlug=google-thirty-days


Given an array nums of n integers, your task is to find the maximum value of k for which there exist two adjacent subarrays of length k each, 
such that both subarrays are strictly increasing. Specifically, check if there are two subarrays of length k starting at indices a and b (a < b), where:

Both subarrays nums[a..a + k - 1] and nums[b..b + k - 1] are strictly increasing.
The subarrays must be adjacent, meaning b = a + k.
Return the maximum possible value of k.

A subarray is a contiguous non-empty sequence of elements within an array.

 

Example 1:

Input: nums = [2,5,7,8,9,2,3,4,3,1]

Output: 3

Explanation:

The subarray starting at index 2 is [7, 8, 9], which is strictly increasing.
The subarray starting at index 5 is [2, 3, 4], which is also strictly increasing.
These two subarrays are adjacent, and 3 is the maximum possible value of k for which two such adjacent strictly increasing subarrays exist.
Example 2:

Input: nums = [1,2,3,4,4,4,4,5,6,7]

Output: 2

Explanation:

The subarray starting at index 0 is [1, 2], which is strictly increasing.
The subarray starting at index 2 is [3, 4], which is also strictly increasing.
These two subarrays are adjacent, and 2 is the maximum possible value of k for which two such adjacent strictly increasing subarrays exist.


Note:

"""

class Solution:
    def maxIncreasingSubarrays(self, nums: List[int]) -> int:
        maxLn = 1
        prev,curr = 1, 1
        for i in range(0, len(nums)-1):
            if nums[i+1]>nums[i]:
                curr+=1
            else:
                # to get max len we can compare min between current and previous length but also
                # curr array we can devide into two with each strictly increasing.for that max(prev,curr//2)
                maxLn = max(maxLn, min(curr,max(prev,curr//2)))
                prev = curr
                curr =1
        maxLn = max(maxLn, min(curr,max(prev,curr//2)))
        print(maxLn)
        return maxLn
        
