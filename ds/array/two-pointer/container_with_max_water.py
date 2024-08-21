"""
https://leetcode.com/problems/container-with-most-water/description/

You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]).

Find two lines that together with the x-axis form a container, such that the container contains the most water.

Return the maximum amount of water a container can store.

Notice that you may not slant the container.
"""

class Solution:
    def maxArea(self, height: List[int]) -> int:
        res = float('-inf')
        if len(height) < 2:
            return 0
        
        i = 0
        j = len(height) - 1
        while i < j:
            dist = j - i
            curr_capacity = min(height[i],height[j]) * dist
            res = max(res,curr_capacity)
            if height[i] > height[j]:
                j -= 1
            else:
                i += 1
        return res





