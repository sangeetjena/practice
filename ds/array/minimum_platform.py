# Given the arrival and departure times of all trains that reach a railway station, the task is to find
# the minimum number of platforms required for the railway station so that no train waits.
# We are given two arrays that represent the arrival and departure times of trains that stop.
#
# Input: arr[] = {9:00, 9:40, 9:50, 11:00, 15:00, 18:00}, dep[] = {9:10, 12:00, 11:20, 11:30, 19:00, 20:00}
# Output: 3
# Explanation: There are at-most three trains at a time (time between 9:40 to 12:00)
#
# Input: arr[] = {9:00, 9:40}, dep[] = {9:10, 12:00}
# Output: 1
# Explanation: Only one platform is needed.
# The idea is to take every interval one by one and find the number of intervals that overlap with it.
# Keep track of the maximum number of intervals that overlap with an interval. Finally, return the maximum value.

def minimum_platform(arr, dept):
    arr = sorted(arr)
    dept = sorted(dept)
    i=j=0
    maxplat = 0
    cnt = 0
    while i<len(arr) and j < len(arr):
        if dept[j]>arr[i]:
            cnt +=1
            maxplat = max(maxplat, cnt)
            i+=1
        else:
            j+=1
            cnt = 0
    return maxplat

print(minimum_platform([900, 940],[910,1200]))
#output - 1

print(minimum_platform([900, 940, 950, 1100, 1500, 1800],[910, 1200, 1120, 1130, 1900, 2000]))
#output - 3