"""
https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/description/

Given an array of integers nums sorted in non-decreasing order, find the starting and ending position of a given target value.

If target is not found in the array, return [-1, -1].

You must write an algorithm with O(log n) runtime complexity.

 

Example 1:

Input: nums = [5,7,7,8,8,10], target = 8
Output: [3,4]

"""
class Solution:
    def searchRange(self, nums: List[int], target: int) -> List[int]:
        
        def binSearch(nums, target, moveleft):
            index = -1
            left = 0
            right = len(nums)-1
            while left <= right:
                mid = (left + right)//2
                print(mid, nums[mid], target)
                if nums[mid] > target:
                    right = mid-1
                elif nums[mid]<target:
                    left = mid+1
                else:
                    print(mid)
                    index = mid
                    if moveleft:
                        right = mid-1
                    else:
                        left = mid +1
            return index
                    
        lft = binSearch(nums, target, True)
        
        right = binSearch(nums, target, False)
        return [lft, right]
