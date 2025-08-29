"""
https://leetcode.com/problems/longest-well-performing-interval/description/

We are given hours, a list of the number of hours worked per day for a given employee.

A day is considered to be a tiring day if and only if the number of hours worked is (strictly) greater than 8.

A well-performing interval is an interval of days for which the number of tiring days is strictly larger than the number of non-tiring days.

Return the length of the longest well-performing interval.

 

Example 1:

Input: hours = [9,9,6,0,6,6,9]
Output: 3
Explanation: The longest well-performing interval is [9,9,6].
Example 2:

Input: hours = [6,6,6]
Output: 0

Note: target is the sub array where there is more +ve value than -ve  (pre-process: make all >8 to +1 and all value <8 = -ve)
1- if total is +ve that means from 0 index to ith index all overal more +ve elements are there than -ve to take index i
2- if total sum is negetive search for even lesser value than total.
   why : from that smaller value it reached to the larger value at index position i becuase there more larger value cames than -ve ,
   that why the total at i position becomer larger than it total-1 value
"""

class Solution:
    def longestWPI(self, hours: List[int]) -> int:
        prefix_sum = {}
        total = 0 
        hours = [1 if hour >8 else -1 for hour in hours]
        max_len = 0
        for i in range(len(hours)):
            total += hours[i]
            # if total is +ve that means from 0 index to ith index all overal more +ve elements are there than -ve to take index i
            if total > 0:
                max_len = max(max_len, i +1)
            # if total sum is negetive search for less value than total
            # why : from that smaller value it reached to the larger value at index position i becuase there more larger value cames than -ve that why the total at i position becomer larger than it total-1 value.
            elif total -1 in prefix_sum.keys():
                max_len = max(max_len, i-prefix_sum[total-1])
            if total not in prefix_sum.keys():
                prefix_sum[total] = i
            
        return max_len


        
