"""
https://leetcode.com/problems/merge-intervals/

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
        
