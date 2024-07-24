"""
https://leetcode.com/problems/permutations/
back tracking
"""

class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        finallist = []
        lst = []
        def allpermute(lst):
            if lst not in finallist and len(lst)== len(nums):
                finallist.append(lst)
            for x in nums:
                if x not in lst:
                    allpermute(lst+[x])
        allpermute(lst)
        print(finallist)
        return finallist
