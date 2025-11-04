"""
https://leetcode.com/problems/squares-of-a-sorted-array/description/

https://www.youtube.com/watch?v=FPCZsG_AkUg

Given an integer array nums sorted in non-decreasing order, return an array of the squares of each number sorted in non-decreasing order.

 

Example 1:

Input: nums = [-4,-1,0,3,10]
Output: [0,1,9,16,100]
Explanation: After squaring, the array becomes [16,1,0,9,100].
After sorting, it becomes [0,1,9,16,100].
Example 2:

Input: nums = [-7,-3,2,3,11]
Output: [4,9,9,49,121]

Note: as the array is sorted, so the bigest -ve element will be at index 0 and bigest +ve num will be there at extream right.
so if so if the square value of two pointer (l,r) will be bigger then place that will be the greatest element in the entire array and place it in the extream right in result array and move the pointer which was biggest.
"""

class Solution:
    def sortedSquares(self, nums: List[int]) -> List[int]:
        start = 0
        end = len(nums)-1
        arr =[0]*(len(nums))
        hindex = end
        while start <= end:
            p= nums[start]**2
            p2 = nums[end]**2
            if start == end:
                arr[hindex] = p
                break
            if p > p2:
                arr[hindex] = p
                start+=1
            else:
                arr[hindex] = p2
                end-=1
            hindex-=1
        return arr
                

        
