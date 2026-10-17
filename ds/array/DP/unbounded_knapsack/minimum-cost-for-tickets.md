```
https://leetcode.com/problems/minimum-cost-for-tickets/description/

You have planned some train traveling one year in advance. The days of the year in which you will travel are given as an integer array days. Each day is an integer from 1 to 365.

Train tickets are sold in three different ways:

a 1-day pass is sold for costs[0] dollars,
a 7-day pass is sold for costs[1] dollars, and
a 30-day pass is sold for costs[2] dollars.
The passes allow that many days of consecutive travel.

For example, if we get a 7-day pass on day 2, then we can travel for 7 days: 2, 3, 4, 5, 6, 7, and 8.
Return the minimum number of dollars you need to travel every day in the given list of days.


Note: create dp and keep place for all the dates.
if the date in dp is not within the days list then simply carry forward the just previous visited date dp[i] = dp[i-1]
else find the min between ticket for day 1,7 and 30 and also add cost to each date range you are taking.
```
<img width="742" height="469" alt="image" src="https://github.com/user-attachments/assets/99d85c14-7961-4f86-914f-7e268e6d7498" />

``` python
# optimization: binary search
from bisect import bisect_right
class Solution:
    def mincostTickets(self, days: list[int], costs: list[int]) -> int:
        dp = [float("inf")]*(len(days)+1)
        dp[0] = 0
        period = [1,7,30]
        for i in range(1, len(days)+1):
            res = float("inf")
            for j in range(len(costs)):
                # search for just previous days where out side of current period boundary
                searchval =  days[i-1]-period[j] if  days[i-1]-period[j]>= 0 else 0 
                index = bisect_right(days,searchval,0,i-1)
                res = min(res, dp[index] + costs[j])
            dp[i] = res
        print(dp)
        return dp[-1]

```
``` python
# here issue is that , we have to create index for all the days in dp irrespective of he is travelling on that day or not. 
class Solution:
    def mincostTickets(self, days: List[int], costs: List[int]) -> int:
        # create entry for all date range either travelling date or not. idea is non travelling date will simply hold the min cost of last visited date to avoid search.
        dp = [0 for _ in range(days[-1]+1)]
        for i in range(1, days[-1]+1):
            # for non visited date cost will be cost of last visited date only
            if i not in days:
                dp[i] = dp[i-1]
            else:
                # by substracting 1,7 or 30 days from todays visited date it will land in either one of the previous visited date or non visited date. 
                # but we have already captured for nonvisited date ( cost of previous visited date i.e dp[i] = dp[i-1]), 
                # so if it will land in any non visited date then it will pull cost of last visited date and if it land in any visited date then that is the border line date then
                # simply take the min ticket cost on that date.
                dp[i] = min(
                    (costs[0]+ dp[max(0, i-1)]), 
                    (costs[1]+ dp[max(0, i-7)]),
                    (costs[2]+ dp[max(0, i-30)])
                )
        print(dp)
        return dp[-1]
```

