```
https://leetcode.com/problems/maximum-profit-in-job-scheduling/description/

Note: fibonanchi dp pattern
similar questions: max non overlapping wage, car-pooling max profit 
```
<img width="1297" height="1055" alt="image" src="https://github.com/user-attachments/assets/8261c420-1141-4791-af5d-964d3a6bdf72" />



``` python
from bisect import bisect_right
class Solution:
    def jobScheduling(self, startTime: list[int], endTime: list[int], profit: list[int]) -> int:
        # converting multi index to single tuple 
        jobs = zip(startTime, endTime, profit)
        jobs = sorted(jobs, key=lambda job: job[1])
        ends = [end for start, end, revenue in jobs]

        n = len(jobs)
        dp = [0] * (n + 1)

        for i in range(1, n + 1):
            start, end, revenue = jobs[i - 1]

            # Number of earlier jobs ending at or before this start.
            compatible_index = bisect_right(ends, start, 0, i - 1)
            # if the present value i am not taking then the immediate previous value i can take
            skip = dp[i - 1]
            # if present value i will take then i can only take just previous value which is not intersecting with the present value.
            take = revenue + dp[compatible_index]

            dp[i] = max(skip, take)

        return dp[-1]

```
