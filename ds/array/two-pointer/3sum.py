"""
https://leetcode.com/problems/3sum/
https://www.youtube.com/watch?v=jzZsG8n2R9A

"""
class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        lst = []
        nums= sorted(nums)
        for i in range(len(nums)):
             # to eleminate dupicate sets in the result sets
            if i>0 and nums[i] == nums[i-1]:
                continue
            l, r = i+1, len(nums)-1
            while l< r:
                # to eleminate dupicate sets in the result sets
                if l>i+1 and nums[l] == nums[l-1]:
                    l+=1
                    continue

                res = nums[i] + nums[l] + nums[r]
                if res == 0:
                    lst.append([nums[i], nums[l], nums[r]])
                    l+=1
                elif res>0:
                    r-=1
                else:
                    l+=1
        return lst
