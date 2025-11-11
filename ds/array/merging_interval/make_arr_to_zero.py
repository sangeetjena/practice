"""
https://leetcode.com/problems/zero-array-transformation-i/description/?envType=company&envId=google&favoriteSlug=google-thirty-days

You are given an integer array nums of length n and a 2D array queries, where queries[i] = [li, ri].

For each queries[i]:

Select a subset of indices within the range [li, ri] in nums.
Decrement the values at the selected indices by 1.
A Zero Array is an array where all elements are equal to 0.

Return true if it is possible to transform nums into a Zero Array after processing all the queries sequentially, otherwise return false.

 

Example 1:

Input: nums = [1,0,1], queries = [[0,2]]

Output: true

Explanation:

For i = 0:
Select the subset of indices as [0, 2] and decrement the values at these indices by 1.
The array will become [0, 0, 0], which is a Zero Array.
Example 2:

Input: nums = [4,3,2,1], queries = [[1,3],[0,2]]

Output: false

Explanation:

For i = 0:
Select the subset of indices as [1, 2, 3] and decrement the values at these indices by 1.
The array will become [4, 2, 1, 0].
For i = 1:
Select the subset of indices as [0, 1, 2] and decrement the values at these indices by 1.
The array will become [3, 1, 0, 0], which is not a Zero Array.

Solution:  https://www.youtube.com/watch?v=hOEg26zHlco
Note: 
soln 1: (using prefix sum)
      1- create difference set, same as curporate ticket booking.(add oposite weightabe at the end of index range)
      after increament value for a sub set all the difference in value of the subset will remain same, 
      so we can say for a subset what really change is starting element of the subset and end +1 element in the subset.
      2- after all the operation if cumilative difference eqal to the element , then the ele,ent can become 0.
soln 2: using merge interval:
    1- find common interval and add frequency as many intersection point came.
    2- use a single loop substract the value from the array.
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

        
