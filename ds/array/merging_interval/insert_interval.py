"""
https://leetcode.com/problems/insert-interval/

You are given an array of non-overlapping intervals intervals where intervals[i] = [starti, endi] represent the start and the end of the ith interval 
and intervals is sorted in ascending order by starti. You are also given an interval newInterval = [start, end] that represents the start and end of another interval.

Insert newInterval into intervals such that intervals is still sorted in ascending order by starti and intervals still does not have any overlapping intervals 
(merge overlapping intervals if necessary).

Return intervals after the insertion.

Note that you don't need to modify intervals in-place. You can make a new array and return it.

 

Example 1:

Input: intervals = [[1,3],[6,9]], newInterval = [2,5]
Output: [[1,5],[6,9]]
Example 2:

Input: intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]
Output: [[1,2],[3,10],[12,16]]
Explanation: Because the new interval [4,8] overlaps with [3,5],[6,7],[8,10].

"""

class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        end = 0
        stack = []
        intervals = intervals + [newInterval]
        intervals.sort()
        print(intervals)
        while end < len(intervals):
            
            if len(stack) == 0:
                stack.append(intervals[end])
                end+=1
                continue
            s = stack[-1][0]
            e = stack[-1][1]
            s1 = intervals[end][0]
            e1 = intervals[end][1]
            print(stack[-1], intervals[end])
            if (s>=s1 and s<=e1) or (e>=s1 and e<=e1) or (s1>=s and s1<=e) or (e1>=s and e1<=e):
                stack[-1] = [min(s,s1), max(e,e1)]
            else:
                stack.append(intervals[end])
            end+=1
        return stack
        
