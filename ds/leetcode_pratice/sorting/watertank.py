"""
11. Container With Most Water
Medium
24.4K
1.3K
company
Microsoft
company
Google
company
Adobe
You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]).

Find two lines that together with the x-axis form a container, such that the container contains the most water.

Return the maximum amount of water a container can store.

Notice that you may not slant the container.



Example 1:



"""
class Solution:
    def maxArea(self, height: List[int]) -> int:
        maxvol = 0
        for i in range(len(height)):
            currvol = 0
            currheight = height[i]
            print(currheight)
            for j in range(i+1,len(height)):
                nextheight = height[j]
                currvol = min(currheight, nextheight)*(j-i)
                if currvol > maxvol:
                    maxvol = currvol
        return maxvol