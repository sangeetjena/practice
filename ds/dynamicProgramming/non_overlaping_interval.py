"""
there is a time seties of interval. find how many interval to remove to make all set as non overlapping interval
"""
from typing import List


class Solution:
    def findMinArrowShots(self, points: List[List[int]]) -> int:
        tmpList = sorted(points)
        arrowCnt = 0
        i = 0
        j=0
        while i< len(tmpList) and j< len(tmpList):
            if (i == j):
                j = j+1
                continue
            s = tmpList[i][0]
            e = tmpList[i][1]
            s1 = tmpList[j][0]
            e1 = tmpList[j][1]
            if (s1 in range(s,e+1) or e1 in range(s,e+1)):
                print("intersect {}, {}".format((s,e),(s1,e1)))
                j+=1
            else:
                i=j
                arrowCnt+=1
        return arrowCnt + 1

obj= Solution()
print(obj.findMinArrowShots([[0,6],[2,6],[4,6],[6,8]]))
