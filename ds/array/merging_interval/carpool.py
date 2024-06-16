"""
https://leetcode.com/problems/car-pooling/
"""

class Solution:
    def carPooling(self, trips: List[List[int]], capacity: int) -> bool:
        tin = [[x[1], x[0]] for x in trips]
        tout = [[x[2], x[0]] for x in trips]
        tin.sort()
        tout.sort()
        s=e=count = 0
        while s<len(tin) and e < len(tout):
            if tout[e][0] > tin[s][0]:
                count+=tin[s][1]
                s+=1
            else:
                count-=tout[e][1]
                e+=1
            if count > capacity:
                return False
        return True
