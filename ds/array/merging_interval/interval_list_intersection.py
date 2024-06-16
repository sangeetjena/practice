"""
https://leetcode.com/problems/interval-list-intersections/description/

"""

class Solution:
    def intervalIntersection(self, firstList: List[List[int]], secondList: List[List[int]]) -> List[List[int]]:
        first = second = 0
        intersection = []
        # simillar to platform problem.
        while first < len(firstList) and second < len(secondList):
            fs = firstList[first][0]
            fe = firstList[first][1]
            ss = secondList[second][0]
            se = secondList[second][1]
            if ((fs >= ss and fs <= se) or (fe >= ss and fe <= se)) or ((ss >= fs and ss <= fe) or (se >= fs and se <= fe)):
                intersection.append([max(fs, ss), min(fe, se)])
            if firstList[first][1] > secondList[second][1]:
                second+=1
            else:
                first+=1
        return intersection
        
