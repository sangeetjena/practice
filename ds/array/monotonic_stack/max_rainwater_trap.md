```
https://leetcode.com/problems/trapping-rain-water/description/

Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.

 

Example 1:


Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6
Explanation: The above elevation map (black section) is represented by array [0,1,0,2,1,0,1,3,2,1,2,1]. In this case, 6 units of rain water (blue section) are being trapped.
Example 2:

Input: height = [4,2,0,3,2,5]
Output: 9

Note:
this problem can be solved using monotonic stack or by using two list one looking to its
left and other look to its right.

in  monotonic stack stack will store the value if value is strictly decreasing ,
if encounter greater value then pop the top element.
that means elements left in the stack after removing top elements will be strictly greater.

```
<img width="441" height="206" alt="image" src="https://github.com/user-attachments/assets/c2333117-4c07-4bb4-9c39-a9eb634afb8a" />

``` python
class Solution:
    def trap(self, height: List[int]) -> int:
        # monotonic stack
        stack = []
        maxWater = 0
        for i in range(len(height)):
            while len(stack) > 0 and height[stack[-1]] <= height[i]:
                top = stack[-1]
                del stack[-1]
                # if no element are there that means no bigger element are there in the stack
                # that means we can't store the water. so break the loop and continue with other walls
                if len(stack) <= 0:
                    break
                # space will be created between previous hightest value of the current popped element and
                # element in the i th position.
                maxheight = min(height[stack[-1]], height[i]) - height[top]
                # why stack[-1] not top, because top contain previous smaller wall but stack[-1] will give its
                # previous highest wall, which we need to store water between previous and next greater wall
                width = i - (stack[-1] + 1)
                maxWater += (maxheight * width)
            stack.append(i)
        return maxWater
```
