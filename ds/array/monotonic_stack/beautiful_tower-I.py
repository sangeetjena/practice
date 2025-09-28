"""
https://leetcode.com/problems/beautiful-towers-i/description/?envType=problem-list-v2&envId=monotonic-stack

You are given an array heights of n integers representing the number of bricks in n consecutive towers. Your task is to remove some bricks to form a mountain-shaped 
tower arrangement. In this arrangement, the tower heights are non-decreasing, reaching a maximum peak value with one or multiple consecutive towers and then non-increasing.

Return the maximum possible sum of heights of a mountain-shaped tower arrangement.

 

Example 1:

Input: heights = [5,3,4,1,1]

Output: 13

Explanation:

We remove some bricks to make heights = [5,3,3,1,1], the peak is at index 0.

Example 2:

Input: heights = [6,5,3,9,2,7]

Output: 22

Explanation:

We remove some bricks to make heights = [3,3,3,9,2,2], the peak is at index 3.


Note: take a mid point and find total upto the mid point considering strinctly increasing monotonic stack and then from mid point to end consider strinctly decreasing monotonic stack.

"""

class Solution:
    def maximumSumOfHeights(self, heights: List[int]) -> int:
        #tricky solution, can be solved using monotonic stack
        # here if we will take a pick value and all the value to its left whould be strictly increasing 
        # and all the value to its right should be strictly decreasing then this problem can be solved using monotonic stack.
        maxsum = 0
        # find the highest number in the array
        maxind = 0
        for i in range(len(heights)):
            maxind = i
            totalsum = 0
            # loop for strictly increasing stack
            stack = []
            for i in range(0,maxind):
                minind = i
                while stack and heights[i] < stack[-1][2]:
                    p,k,j = stack[-1]
                    del stack[-1]
                    minind = p
                stack.append((minind,i,heights[i]))
            while stack:
                x,y,z = stack[-1]
                del stack[-1]
                totalsum+= z * (y-x + 1)
            # loop from highest index value to right and strictly decreasing
            prev_height = heights[maxind]
            totalsum += heights[maxind]
            for i in range(maxind+1, len(heights)):
                if heights[i]> prev_height:
                    totalsum+=prev_height
                else:
                    totalsum+=heights[i]
                    prev_height = heights[i]
            maxsum = max(maxsum, totalsum)
        return maxsum
            
        
        
        

            
        



        
