"""
https://leetcode.com/problems/subsets-ii/

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
