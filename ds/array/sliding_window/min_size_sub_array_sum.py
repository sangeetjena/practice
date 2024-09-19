"""
https://leetcode.com/problems/minimum-size-subarray-sum/

Given an array of positive integers nums and a positive integer target, return the minimal length of a 
subarray
 whose sum is greater than or equal to target. If there is no such subarray, return 0 instead.

 

Example 1:

Input: target = 7, nums = [2,3,1,2,4,3]
Output: 2
Explanation: The subarray [4,3] has the minimal length under the problem constraint.

Note: if sum is greater than target don't let end pointer increase

"""
class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        s=0
        e=0
        sm = 0
        mn_ln = 999999
        while e<len(nums):
            sm+=nums[e]
            # if found sum is greater than or equals to target then keep removing the elements untill sum is less than target.
            while sm>=target:
                mn_ln = min(mn_ln, e-s+1)
                sm-= nums[s]
                s+=1
            e+=1
        print(mn_ln)
        return mn_ln if mn_ln != 999999 else 0



