"""
https://leetcode.com/problems/zero-array-transformation-i/description/?envType=company&envId=google&favoriteSlug=google-thirty-days

Solution:  https://www.youtube.com/watch?v=hOEg26zHlco
Note: create difference set, same as curporate ticket booking.(add oposite weightabe at the end of index range)
      after increament value for a sub set all the difference in value of the subset will remain same, 
      so we can say for a subset what really change is starting element of the subset and end +1 element in the subset.
      2- after all the operation if cumilative difference eqal to the element , then the ele,ent can become 0.
"""
class Solution:
    def isZeroArray(self, nums: List[int], queries: List[List[int]]) -> bool:
        arr = [0 for i in range(len(nums))]
        for l,r in queries:
            arr[l]+=1
            if r<len(nums)-1:
                arr[r+1]-=1
        for i in range(len(nums)):
            if arr[i] < nums[i]:
                return False
            if i<len(nums)-1:
                arr[i+1] = arr[i+1] + arr[i]
        return True

        
