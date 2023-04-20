"""
Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.

The overall run time complexity should be O(log (m+n)).



Example 1:

Input: nums1 = [1,3], nums2 = [2]
Output: 2.00000
Explanation: merged array = [1,2,3] and median is 2.
Example 2:

Input: nums1 = [1,2], nums2 = [3,4]
Output: 2.50000
Explanation: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.

"""
from typing import List


class Solution:
    def bobbleSort(self, arr, element):
        min = 0
        max = len(arr) - 1
        for i in range(len(arr)):
            if element > arr[max]:
                arr.append(element)
                return arr
            if element < arr[min]:
                arr = [element] + arr
                return arr
            if (max - min) == 1:
                arr = arr[: min +1] + [element] + arr[max:]
                return arr
            median = round((min + max) / 2)
            if element > arr[median]:
                min = median
            else:
                max = median

    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        len1 = len(nums1)
        len2 = len(nums2)
        arr1 = []
        arr2 = []
        if len1 > len2:
            arr1 = nums1
            arr2 = nums2
        else:
            arr1 = nums2
            arr2 = nums1
        if len1 == 0 or len2 ==0:
            arr1 = arr1 + arr2
        else:
            for element in arr2:
                arr1 = self.bobbleSort(arr1, element)
                print(arr1)
        if (len(arr1)) % 2 == 0:
            idx = round((len(arr1)) / 2)
            print(idx)
            return ((arr1[idx-1] + arr1[idx]) / 2)
        else:
            idx = round((len(arr1)+1) / 2)
            print(idx -1)
            return ((arr1[idx - 1]))




obj = Solution()
result = obj.findMedianSortedArrays([], [1,2,3,4,5])
print(result)