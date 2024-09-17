"""
https://leetcode.com/problems/4sum/description/
https://www.youtube.com/watch?v=EYeR-_1NRlQ

Note: similar to 3sum or trangle add another outer loop.
"""

class Solution:
    def fourSum(self, nums: List[int], target: int) -> List[List[int]]:
        dp = []
        nums.sort()
        for i in range(len(nums)-3):
            for j in range(i+1, len(nums)-2):
                l=j+1
                r = len(nums)-1
                while(l<r):
                    sm = sum([nums[i], nums[j], nums[l], nums[r]])
                    st = [nums[i], nums[j], nums[l], nums[r]]
                    if sm == target :
                        if st not in dp:
                            dp.append(st)
                    if sm<target:
                        l+=1
                    else:
                        r-=1
        return dp

