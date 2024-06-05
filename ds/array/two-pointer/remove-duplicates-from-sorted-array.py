"""
https://leetcode.com/problems/remove-duplicates-from-sorted-array/description/
"""

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
