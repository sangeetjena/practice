"""
https://leetcode.com/problems/subsets/
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
        
        
