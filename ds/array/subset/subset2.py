"""
https://leetcode.com/problems/subsets-ii/

Given an integer array nums that may contain duplicates, return all possible subsets (the power set).

The solution set must not contain duplicate subsets. Return the solution in any order.

 

Example 1:

Input: nums = [1,2,2]
Output: [[],[1],[1,2],[1,2,2],[2],[2,2]]
Example 2:

Input: nums = [0]
Output: [[],[0]]


"""

class Solution:
    def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:
        # using backtracking
        # similar to subsets 1
        finallist = []
        index = -1
        lst = []
        nums=sorted(nums)
        def findsubset(lst, index):
            if lst not in finallist:
                finallist.append(lst)
            index+=1
            if index >= len(nums):
                return
            findsubset(lst+[nums[index]], index)
            findsubset(lst, index)
        findsubset(lst,index)
        return finallist
