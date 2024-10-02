"""
https://leetcode.com/problems/minimum-cost-for-tickets/description/


Note: create dp and keep place for all the dates.
if the date in dp is not within the days list then simply carry forward the just previous visited date dp[i] = dp[i-1]
else find the min between ticket for day 1,7 and 30 and also add cost to each date range you are taking.
"""
class Solution:
    def mincostTickets(self, days: List[int], costs: List[int]) -> int:
        dp = [0 for _ in range(days[-1]+1)]
        for i in range(1, days[-1]+1):
            # for non visited date cost will be cost of last visited date only
            if i not in days:
                dp[i] = dp[i-1]
            else:
                # by substracting 1,7 or 30 days from todays visited date it will land in either one of the previous visited date or non visited date. but we have already captured for nonvisited date ( cost of previous visited date i.e dp[i] = dp[i-1]), so if it will land in any non visited date then it will pull cost of last visited date and if it land in any visited date then that is the border line date then simply take the min ticket cost on that date.
                dp[i] = min(
                    (costs[0]+ dp[max(0, i-1)]), 
                    (costs[1]+ dp[max(0, i-7)]),
                    (costs[2]+ dp[max(0, i-30)])
                )
        print(dp)
        return dp[-1]
