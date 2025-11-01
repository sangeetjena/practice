"""
https://leetcode.com/problems/maximum-length-of-repeated-subarray/solutions/2600837/python-simple-python-solution-using-dynamic-programming/

Given two integer arrays nums1 and nums2, return the maximum length of a subarray that appears in both arrays.

 

Example 1:

Input: nums1 = [1,2,3,2,1], nums2 = [3,2,1,4,7]
Output: 3
Explanation: The repeated subarray with maximum length is [3,2,1].
Example 2:

Input: nums1 = [0,0,0,0,0], nums2 = [0,0,0,0,0]
Output: 5
Explanation: The repeated subarray with maximum length is [0,0,0,0,0].

Note:
bruite force : take two pointer and take one position from num1 and check in num2 continue till find missmatch, then reset 1st pointer and start from 
begining for 2nd array 


"""

class Solution:
    def findLength(self, nums1: List[int], nums2: List[int]) -> int:
        dp = [[0 for i in range(len(nums1)+1)] for _ in range(len(nums2)+1)]
        max_len = 0
        for i in range(1,len(nums2)+1):
            for j in range(1,len(nums1)+1):
				# for longest sub array current value should match and its previous index value also should match.
                if nums2[i-1] == nums1[j-1]:
                    dp[i][j] = 1+dp[i-1][j-1]
                    max_len = max(max_len, dp[i][j])
        return max_len
        
