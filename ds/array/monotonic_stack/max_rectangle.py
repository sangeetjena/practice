"""
https://leetcode.com/problems/largest-rectangle-in-histogram/description/?envType=problem-list-v2&envId=monotonic-stack

Note:

"""
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        stack  = []
        maxval  = 0 
        # extract and evalute all value if we encounter a smaller value 
        for i in range(len(heights)):
            minindex = i
            while stack and heights[stack[-1][0]] >= heights[i]:
                print(heights[stack[-1][0]])
                maxval = max(maxval, (i-stack[-1][1])*heights[stack[-1][0]], heights[i])
                minindex = min(minindex,stack[-1][1])
                del stack[-1]
            stack.append([i,minindex])
        # if any element left in the stack that means it is strictly increasing. so calulate area by
        # current height * (len of array) - (min index stored at at that position )
            print("---")
            print(maxval)
        while stack:
            maxval = max( maxval , (len(heights)-stack[-1][1])*heights[stack[-1][0]])
            del stack[-1]
        return maxval
                
        

        

        


        
