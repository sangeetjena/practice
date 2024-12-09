"""
similar to adjacent increasing subarray 1
https://leetcode.com/problems/adjacent-increasing-subarrays-detection-ii/description/?envType=company&envId=google&favoriteSlug=google-thirty-days


"""

class Solution:
    def maxIncreasingSubarrays(self, nums: List[int]) -> int:
        maxLn = 1
        prev,curr = 1, 1
        for i in range(0, len(nums)-1):
            if nums[i+1]>nums[i]:
                curr+=1
            else:
                # to get max len we can compare min between current and previous length but also
                # curr array we can devide into two with each strictly increasing.for that max(prev,curr//2)
                maxLn = max(maxLn, min(curr,max(prev,curr//2)))
                prev = curr
                curr =1
        maxLn = max(maxLn, min(curr,max(prev,curr//2)))
        print(maxLn)
        return maxLn
        
