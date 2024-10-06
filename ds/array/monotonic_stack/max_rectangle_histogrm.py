"""
https://leetcode.com/problems/largest-rectangle-in-histogram/

Note: slightly different than water tank. as in water tank we are extracting all low heights once got a higher height to form a hollow to store water.
but in this case it is oposite, we are extracting all hight once got on low to form a solid rectangle.

"""
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        stack = []
        maxarea = 0
        for i in range(len(heights)):
            ind=i
            # extract all bigger heights once get a smaller height and calculate area upto the curent index
            while len(stack)>0 and stack[-1][1]>heights[i]:
                ind,h = stack.pop()
                maxarea = max(maxarea, h*(i-ind))  
            # if no smaller index found i.e not enter the while loop then store current index and height
            # else store the min index of all the higher height for the current height.
            # why ? because current small value can for rectangle upto previous high blocks
            stack.append((ind,heights[i]))
        # if stack is not empty then all strictly increasing heights are there. and we will find area
        # between (i upto end of array length)* height.
        while len(stack)>0:
            ind,h = stack.pop()
            maxarea = max(maxarea, ((len(heights))-ind)*h)
        return maxarea
