"""
https://leetcode.com/problems/buildings-with-an-ocean-view/description/

There are n buildings in a line. You are given an integer array heights of size n that represents the heights of the buildings in the line.

The ocean is to the right of the buildings. A building has an ocean view if the building can see the ocean without obstructions. Formally, a building has an ocean view if all the buildings to its right have a smaller height.

Return a list of indices (0-indexed) of buildings that have an ocean view, sorted in increasing order.

 

Example 1:

Input: heights = [4,2,3,1]
Output: [0,2,3]
Explanation: Building 1 (0-indexed) does not have an ocean view because building 2 is taller.

"""

class Solution:
    def findBuildings(self, heights: List[int]) -> List[int]:
        dp = [0 for i in range(len(heights))]
        dp[-1] = 0
        stack = []
        for i in range(len(heights)):
            while len(stack)>0 and heights[stack[-1]]<= heights[i]:
                dp[stack[-1]] = -1
                stack.pop()
            stack.append(i)
        return [i for i in range(len(heights)) if dp[i]!=-1]

========
class Solution:
    def findBuildings(self, heights: List[int]) -> List[int]:
        dp = [-1 for i in range(len(heights))]
        dp[-1] = 0
        stack = []
        for i in reversed(range(len(heights))):
            while len(stack)>0 and heights[stack[-1]]< heights[i]:
                stack.pop()
            if len(stack) == 0:
                dp[i] = 0
            stack.append(i)
        print(dp)
        return [i for i in range(len(heights)) if dp[i]!=-1]

        
