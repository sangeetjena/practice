```
https://leetcode.com/problems/number-of-visible-people-in-a-queue/description/
1944: Number of visible people in the queue

There are n people standing in a queue, and they numbered from 0 to n - 1 in left to right order. 
You are given an array heights of distinct integers where heights[i] represents the height of the ith person.

A person can see another person to their right in the queue if everybody in between is shorter than both of them. 
More formally, the ith person can see the jth person if i < j and min(heights[i], heights[j]) > max(heights[i+1], heights[i+2], ..., heights[j-1]).

Return an array answer of length n where answer[i] is the number of people the ith person can see to their right in the queue.

```
<img width="627" height="581" alt="image" src="https://github.com/user-attachments/assets/66631c0c-c8f6-49cd-bb9e-12b29880b33a" />


``` python
from typing import List


class Solution:
    def canSeePersonsCount(self, heights: List[int]) -> List[int]:
        maxVis = [0 for i in range(len(heights))]
        stack = []
        for i in reversed(range(len(heights))):
            # if present value is greater than the lat element in the stack then.
            # person in the present height can see person in the top of the stack
            while (len(stack) > 0 and stack[-1] < heights[i]):
                del stack[-1]
                maxVis[i] += 1
            if len(stack) > 0:
                # if stack is not empty then last element is greater than present person height hence
                # prestn person can see the height of the top stack person.
                maxVis[i] += 1
            stack.append(heights[i])
        return maxVis


obj = Solution()
arr = [10,6,8,5,11,9]
print(obj.canSeePersonsCount(arr))
```
