"""
https://leetcode.com/problems/daily-temperatures/description/

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

            
        
