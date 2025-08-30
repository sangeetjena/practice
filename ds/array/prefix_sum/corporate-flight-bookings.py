"""
https://leetcode.com/problems/corporate-flight-bookings/description/

There are n flights that are labeled from 1 to n.

You are given an array of flight bookings bookings, where bookings[i] = [firsti, lasti, seatsi] represents a booking for flights firsti through lasti (inclusive) with seatsi seats reserved for each flight in the range.

Return an array answer of length n, where answer[i] is the total number of seats reserved for flight i.

 

Example 1:

Input: bookings = [[1,2,10],[2,3,20],[2,5,25]], n = 5
Output: [10,55,45,25,25]
Explanation:
Flight labels:        1   2   3   4   5
Booking 1 reserved:  10  10
Booking 2 reserved:      20  20
Booking 3 reserved:      25  25  25  25
Total seats:         10  55  45  25  25
Hence, answer = [10,55,45,25,25]
Example 2:

Input: bookings = [[1,2,10],[2,2,15]], n = 2
Output: [10,25]
Explanation:
Flight labels:        1   2
Booking 1 reserved:  10  10
Booking 2 reserved:      15
Total seats:         10  25
Hence, answer = [10,25]

Note: with simple loop approach time limit will exceed, so optimization is prefix sum.
ref: https://leetcode.com/problems/corporate-flight-bookings/solutions/7129650/flight-seats-made-easy-prefix-sum-trick-for-beginners/
"""
class Solution:
    def corpFlightBookings(self, bookings: List[List[int]], n: int) -> List[int]:
        ans = [0] * (n+1)
        # add value only to the start of the index, then in prefix sum it will add to all its child/ range
        for start, end, value in bookings:
          # why += ?  becaue multiple start index with the same value will exists.
            ans[start] += value
            # if there is any gap in the range then previous value should not carry forward. so substract the value at the end of the range.
            if end < len(ans)-1:
                ans[end+1]-=value

        #apply prefix sum:
        print(ans)
        for i in range(1, len(ans)):
            ans[i] += ans[i-1]
        print(ans)
        return ans[1:]
