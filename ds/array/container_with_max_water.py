"""

"""


class Solution:
    def maxArea(self, height: List[int]) -> int:
        maxwater = 0
        p1 = 1
        p2 = len(height)
        while p1 < p2:
            if maxwater < ((p2 - p1) * min(height[p1 - 1], height[p2 - 1])):
                maxwater = ((p2 - p1) * min(height[p1 - 1], height[p2 - 1]))
            if height[p1 - 1] > height[p2 - 1]:
                p2 -= 1
            else:
                p1 += 1
        return maxwater


"""
class Solution:
    def maxArea(self, height: List[int]) -> int:
        maxwater = 0
        for i in range(0, len(height)-1):
            tempwater = 0
            for j in range(i+1,len(height)):
                if tempwater< (j-i)*min(height[i], height[j]):
                    tempwater =  (j-i)*min(height[i], height[j])
            if maxwater< tempwater:
                maxwater = tempwater
        return maxwater
                    
        
"""