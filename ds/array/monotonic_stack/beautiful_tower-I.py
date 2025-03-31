"""
https://leetcode.com/problems/beautiful-towers-i/description/?envType=problem-list-v2&envId=monotonic-stack

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
            
        
        
        

            
        



        
