"""
https://leetcode.com/problems/remove-duplicates-from-sorted-array/description/

Note: # keep two pointer 
# j pointer increment till get the the 1st non duplicate element and keep i pointer on last swap location
"""

class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        i,j = 1,1
        # keep two pointer 
        # j pointer increment till get the the 1st non duplicate element and keep i pointer on last swap location
        while j< len(nums):
            if nums[j] == nums[j-1]:
                j+=1
                continue
            else:
                nums[i] =  nums[j]
                j+=1
                i+=1
        return i

==========================================

class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        total = len(nums)
        dele = 0
        start=0
        end = 1
        while end < len(nums):
            if nums[start]==nums[end]:
                dele +=1
                del nums[end]
                continue
            start= end
            end+=1
        return total-dele
