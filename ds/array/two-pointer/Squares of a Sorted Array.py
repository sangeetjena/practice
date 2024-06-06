"""
https://leetcode.com/problems/squares-of-a-sorted-array/description/
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
                

        
