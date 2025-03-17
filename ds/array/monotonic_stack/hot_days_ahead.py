"""
https://leetcode.com/problems/daily-temperatures/description/

Given an array of integers temperatures represents the daily temperatures, return an array answer such that answer[i] is the number of days you have to wait after the ith day to get a warmer temperature. If there is no future day for which this is possible, keep answer[i] == 0 instead.

 

Example 1:

Input: temperatures = [73,74,75,71,69,72,76,73]
Output: [1,1,4,2,1,1,0,0]

Note:
use monotonic stack and calculate hot days ahead by substracting current index with index in stack and store it in dp.

"""

class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        dp = [0 for i in range(len(temperatures))]
        stack = []
        for i in range(len(temperatures)):
            while len(stack)!=0 and temperatures[stack[-1]]< temperatures[i]:
                temp = stack.pop()
                dp[temp] = i-temp
            stack.append(i)
        print(dp)
        return dp

            
        
