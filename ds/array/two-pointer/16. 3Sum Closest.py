"""
https://leetcode.com/problems/3sum-closest/description/

"""

class Solution:
    def threeSumClosest(self, nums: List[int], target: int) -> int:
        nums=sorted(nums)

        print(nums)
        prev = 99999
        for i in range(len(nums)):
            l, r = i+1, len(nums)-1
            while l<r:
                res = nums[i] + nums[l] + nums[r]
                if abs(res - target) < abs(prev - target):
                    prev = res
                if res > target:
                    r-=1
                elif res < target:
                    l+=1
                else:
                    return res
        return prev
