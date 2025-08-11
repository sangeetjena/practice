```
https://leetcode.com/problems/largest-rectangle-in-histogram/description/?envType=problem-list-v2&envId=monotonic-stack
Given an array of integers heights representing the histogram's bar height where the width of each bar is 1,
return the area of the largest rectangle in the histogram.


```
Example 1:
<img width="200" height="150" alt="image" src="https://github.com/user-attachments/assets/de47a15f-d23b-4ead-a739-f8c2c5f79381" />

```
Input: heights = [2,1,5,6,2,3]
Output: 10
Explanation: The above is a histogram where width of each bar is 1.
The largest rectangle is shown in the red area, which has an area = 10 units.
Example 2:
```
<img width="200" height="150" alt="image" src="https://github.com/user-attachments/assets/15f38d16-e5f0-4f5f-9e5e-3e81eeb29b93" />

```
Input: heights = [2,4]
Output: 4
 

Constraints:

1 <= heights.length <= 105
0 <= heights[i] <= 104

Note: Monotonic stack problem.

```

```python
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

```
                
        

        

        


        
