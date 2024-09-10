"""
https://leetcode.com/problems/course-schedule/description/


"""

class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        dct = {}
        # create adjacency list
        for key, value in prerequisites:
            if key in dct.keys():
                dct[key].append(value)
            else:
                dct[key] = [value]
        visited, cycle, dfs = [], set(), []
        for key in dct.keys():
            if key in visited:
                continue
            dfs = [key]
            while len(dfs)>0:
                key = dfs[-1]
                cycle.add(key)
                if (key not in dct.keys()) or key in visited:
                    del dfs[-1]
                    cycle.remove(key)
                else:
                    for chld in dct[key]:
                        if chld in cycle:
                            return False
                        dfs.append(chld)
                visited.append(key)
        return True
            
