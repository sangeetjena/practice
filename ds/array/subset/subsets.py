"""
https://leetcode.com/problems/subsets/

Given an integer array nums of unique elements, return all possible subsets (the power set).

The solution set must not contain duplicate subsets. Return the solution in any order.

 

Example 1:

Input: nums = [1,2,3]
Output: [[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]
Example 2:

Input: nums = [0]
Output: [[],[0]]


backtracking
"""

class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        # using back tracking tehnique
        lst = []
        finallist = []
        ind = -1
        num = nums
        def allSets(lst, ind):
            if lst in finallist:
                pass 
            else:
                finallist.append(lst)
            ind+=1
            if ind >= len(num):
                return
            # print(ind, lst, finallist)
            allSets(lst+[num[ind]],ind)
            allSets(lst, ind)
        allSets(lst,ind)
        return finallist
        
        
