"""
Adjacent Increasing Subarrays Detection I
https://leetcode.com/problems/adjacent-increasing-subarrays-detection-i/description/

Note:
take prev and curr, keep increasing curr length untill find a breaking point where eleement is not strictly increasing.
at each breaking point store curr to prev and make crr=1 and check if prev==curr==k or curr >=2*k

"""

class Solution:
    def hasIncreasingSubarrays(self, nums: List[int], k: int) -> bool:
        prev, curr = 1,1
        if len(nums)<k:
            return False
        for i in range(0, len(nums)-1):
            if nums[i+1]> nums[i]:
                curr+=1
            else:
                if curr>=2*k or (prev>=k and curr >=k):
                    return True
                prev = curr
                curr = 1
        print(curr)
        if curr>=2*k or (prev>=k and curr >=k):
                    return True
        return False 
        
