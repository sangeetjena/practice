"""
https://leetcode.com/problems/single-element-in-a-sorted-array/description/?envType=company&envId=google&favoriteSlug=google-thirty-days

Note: clue is find the group where all duplicate elements are there (i.e: len of that group will be even)

"""
class Solution:
    def singleNonDuplicate(self, nums: List[int]) -> int:
        # as in the question mentioned it is a sorted array, it is expected all the element will be in the incresingin corder 
        # this is a two pointer problem. i will take i and i+1 and check if the element present at this indedx are equal or not, if the element are equal i will jump both the pointor to i+1
        # cornor cases : last elemnet in the array could be the unique element !
        # brute force soulution.
        # i=0
        # while i < len(nums):
        #     if i+1 == len(nums) or nums[i] !=nums[i+1]:
        #         return nums[i]
        #     i+=2
        # return False

        # solution using binary search. idea is i will use binary search  i.e: mid = (l+r)/2 /then at the mid i will check 
        # if the duplicate is ther in right side of the middle element or left side based on that i will create two group. as mentioned in teh description that we have exatly two duplicated then the set has all duplicate will have even length and the set has unique element will have odd lenght.
        l ,r = 0, len(nums)-1
        while l<=r:
            mid = (l+r)//2
            if mid<len(nums)-1 and nums[mid] == nums[mid+1]:
                if len(nums[mid:r+1])%2 == 0:
                    r=mid-1
                else:
                    l=mid
                print(nums[l:r+1])
            elif mid>0 and nums[mid] == nums[mid-1]:
                if len(nums[l:mid+1])%2 == 0:
                    l=mid+1
                else:
                    r=mid
                print(nums[l:r+1])
            else:
                return nums[mid]
                 
        
