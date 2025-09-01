"""

https://leetcode.com/problems/valid-triangle-number/description/

Given an integer array nums, return the number of triplets chosen from the array that can make triangles if we take them as side lengths of a triangle.

 

Example 1:

Input: nums = [2,2,3,4]
Output: 3
Explanation: Valid combinations are: 
2,3,4 (using the first 2)
2,3,4 (using the second 2)
2,2,3
Example 2:

Input: nums = [4,2,3,4]
Output: 4

Note:
# sort array 
        # keep one pointer at the highest num
        # keep other other two pointer, on at the beginingn and other next to the bigest element
        # if sum of smaller two is greter than the biggger then all the elments within the range will be bigger
        # else increment small 
"""

class Solution:
    def triangleNumber(self, nums: List[int]) -> int:
        cnt = 0
        nums = sorted(nums)
        # sort array 
        # keep one pointer at the highest num
        # keep other other two pointer, on at the beginingn and other next to the bigest element
        # if sum of smaller two is greter than the biggger then all the elments within the range will be bigger
        # else increment small 
        for k in reversed(range(len(nums))):
            i,j = 0, k-1
            print(i,j,k)
            while i<j:
                if nums[i]+nums[j] > nums[k]:
                    cnt+=(j-i)
                    j-=1
                else:
                    i+=1
        return cnt


        
