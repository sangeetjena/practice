"""
https://leetcode.com/problems/make-sum-divisible-by-p/description/?envType=daily-question&envId=2024-10-03
Given an array of positive integers nums, remove the smallest subarray (possibly empty) such that the sum of the remaining elements is divisible by p. It is not allowed to remove the whole array.

Return the length of the smallest subarray that you need to remove, or -1 if it's impossible.

A subarray is defined as a contiguous block of elements in the array.

 

Example 1:

Input: nums = [3,1,4,2], p = 6
Output: 1
Explanation: The sum of the elements in nums is 10, which is not divisible by 6. We can remove the subarray [4], and the sum of the remaining elements is 6, which is divisible by 6.


Note: sliding window 
optimisation: prefix sum

"""
class Solution:
    def minSubarray(self, nums: List[int], p: int) -> int:
        sm = sum(nums)
        if sm % p == 0:
            return 0
        if p> sm:
            return -1
        mn = float("inf")
        for k in reversed(range(sm//p+1)):
            if k == 0 or mn != float("inf"):
                break
            i,j=0,0
            val = sm-(p*k)
            while j< len(nums):
                if sum(nums[i:j+1])<val:
                    j+=1
                elif sum(nums[i:j+1])== val:
                     mn = min(mn,len(nums[i:j+1]))
                     i+=1
                else:
                    i+=1
        return mn if mn< float("inf") else -1
