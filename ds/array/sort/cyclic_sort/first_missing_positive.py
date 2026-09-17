"""
https://leetcode.com/problems/first-missing-positive/description/

https://www.youtube.com/watch?v=8g78yfzMlao

Given an unsorted integer array nums. Return the smallest positive integer that is not present in nums.

You must implement an algorithm that runs in O(n) time and uses O(1) auxiliary space.

 

Example 1:

Input: nums = [1,2,0]
Output: 3
Explanation: The numbers in the range [1,2] are all in the array.
Example 2:

Input: nums = [3,4,-1,1]
Output: 2
Explanation: 1 is in the array but 2 is missing.
Example 3:

Input: nums = [7,8,9,11,12]
Output: 1
Explanation: The smallest positive integer 1 is missing.

Note: read the comment. we are following in place replacement in the array with an -ve number. 
then check 1st index position where we go a non -ve number (+ve number means that number is missing in the sequence)
so here complexity is O(n)
"""

class Solution:
    def firstMissingPositive(self, nums: List[int]) -> int:
        # convert all negative number out of bound or not include in calculation
        for i in range(len(nums)):
            # discard 0's from calculation
            if nums[i] <=0:
                nums[i] = len(nums)+1
        for i in range(len(nums)):
            if abs(nums[i])> len(nums):
                continue
            if nums[abs(nums[i])-1] >0:
                nums[abs(nums[i])-1] = nums[abs(nums[i])-1]*-1
        print(nums)
        for i in range(len(nums)):
            if nums[i]>=0:
                return i+1
        return len(nums)+1
        
