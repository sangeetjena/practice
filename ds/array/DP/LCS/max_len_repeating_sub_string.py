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



"""

class Solution:
	def findLength(self, nums1: List[int], nums2: List[int]) -> int:

		result = 0

		dp = [[0] * (len(nums2)+1) for _ in range(len(nums1)+1)] 

		for i in range(len(nums1)):

			for j in range(len(nums2)):

				if nums1[i] == nums2[j]:

					new_value = dp[i][j] + 1 

					dp[i+1][j+1] = new_value

					result = max(result, new_value)

		return result
