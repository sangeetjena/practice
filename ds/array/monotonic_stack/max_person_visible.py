"""
1944: Number of visible people in the queue
"""
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