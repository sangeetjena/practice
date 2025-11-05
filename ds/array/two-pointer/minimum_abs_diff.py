"""
https://leetcode.com/problems/minimum-absolute-difference/description/

Given an array of distinct integers arr, find all pairs of elements with the minimum absolute difference of any two elements.

Return a list of pairs in ascending order(with respect to pairs), each pair [a, b] follows

a, b are from arr
a < b
b - a equals to the minimum absolute difference of any two elements in arr
"""
class Solution:
    def minimumAbsDifference(self, arr: List[int]) -> List[List[int]]:
        arr = sorted(arr)
        absdiff = []
        diff = 999
        for i in range(len(arr)-1):
            if arr[i+1]-arr[i]< diff:
                diff = arr[i+1]-arr[i]
                absdiff= [[arr[i],arr[i+1]]]
            elif arr[i+1]-arr[i] == diff:
                absdiff.append([arr[i],arr[i+1]])
        print(absdiff)
        return absdiff
