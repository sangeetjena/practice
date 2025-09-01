"""
https://leetcode.com/problems/meeting-rooms-ii/description/?envType=problem-list-v2&envId=two-pointers

Given an array of meeting time intervals intervals where intervals[i] = [starti, endi], return the minimum number of conference rooms required.

 

Example 1:

Input: intervals = [[0,30],[5,10],[15,20]]
Output: 2
Example 2:

Input: intervals = [[7,10],[2,4]]
Output: 1


Note:
# this is same as platform problem 
# sort the array take arrival and departure 
# put one pointer on the departure and keep incresing arrival pointer, increase counter if arriver ponter is increasing , decrement the conter if departure pointer is increasing 
        
"""

class Solution:
    def minMeetingRooms(self, intervals: List[List[int]]) -> int:
        # this is same as platform problem 
        # sort the array take arrival and departure 
        # put one pointer on the departure and keep incresing arrival pointer, increase counter if arriver ponter is increasing , decrement the conter if departure pointer is increasing 
        arrival = sorted([a[0] for a in intervals],reverse=False)
        departure = sorted([a[1] for a in intervals],reverse=False)
        print(arrival,departure)
        arr, dep = 0,0
        count = 0
        max_room = 0
        while arr < len(intervals) and dep < len(intervals):
            if departure[dep] > arrival[arr]:
                count+=1
                max_room = max(max_room, count)
                arr+=1
            else:
                count -=1 
                dep+=1
        return max_room

        
