"""
https://leetcode.com/problems/permutations/
Given an array nums of distinct integers, return all the possible permutations. You can return the answer in any order.

 

Example 1:

Input: nums = [1,2,3]
Output: [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
Example 2:

Input: nums = [0,1]
Output: [[0,1],[1,0]]
Example 3:

Input: nums = [1]
Output: [[1]]



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


#### using bit masking 

class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        visited = set()
        res = []
        full_mask = 0
        for l in range(len(nums)):
            full_mask = full_mask | 1<<l
        def dfs(mask, lst):
            if mask == full_mask:
                res.append(lst)
                return
            for i in range(len(nums)):
                if ((1<<i) & mask) > 0:
                    continue
                # using lst.append it uses same memory location which will create problen in recurssion but using lst + [] this will create new memory location and will fix same memory allcaition problem in recurssion problem.
                dfs(mask|1<<i, lst + [nums[i]])
        dfs(0,[])
        return res
            

