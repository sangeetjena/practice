"""
https://leetcode.com/problems/merge-intervals/

Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.

 

Example 1:

Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
Explanation: Since intervals [1,3] and [2,6] overlap, merge them into [1,6].
Example 2:

Input: intervals = [[1,4],[4,5]]
Output: [[1,5]]
Explanation: Intervals [1,4] and [4,5] are considered overlapping.
Example 3:

Input: intervals = [[4,7],[1,4]]
Output: [[1,7]]
Explanation: Intervals [1,4] and [4,7] are considered overlapping.

"""
class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        intervals.sort()
        end = 0
        stack = []
        while end < len(intervals):
            if len(stack) == 0:
                stack.append(intervals[end])
                end+=1
                continue
            s = stack[-1][0]
            e = stack[-1][1]
            if (intervals[end][0] >= s and intervals[end][0]<= e) or (intervals[end][1] >= s and intervals[end][1]<= e):
                stack[-1] = [min(intervals[end][0], stack[-1][0]), max(intervals[end][1], stack[-1][1])]
            else:
                stack.append(intervals[end])
            end+=1
        return stack
        
