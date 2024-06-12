"""
https://leetcode.com/problems/insert-interval/

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
        
