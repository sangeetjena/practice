"""
https://leetcode.com/problems/minimum-cost-for-tickets/description/
"""


class Solution:
    def mincostTickets(self, days: List[int], costs: List[int]) -> int:
        dp = {i: 9999 for i in days}
        dp[0] = 0
        cdays = [1, 7, 30]
        for i in range(len(days)):
            for j in range(len(costs)):
                diffdays = days[i] - cdays[j] + 1
                x = [i for i in days if i < diffdays]
                maxdays = 0
                if len(x) > 0:
                    maxdays = max(x)
                dp[days[i]] = min(dp[days[i]], costs[j] + dp[maxdays])
        print(dp)
        return dp[days[-1]]

days = [1,4,6,7,8,20], costs = [2,7,15]


