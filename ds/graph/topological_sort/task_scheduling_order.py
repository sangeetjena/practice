"""
https://leetcode.com/problems/course-schedule/description/
There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1. 
You are given an array prerequisites where prerequisites[i] = [ai, bi] 
indicates that you must take course bi first if you want to take course ai.

For example, the pair [0, 1], indicates that to take course 0 you have to first take course 1.
Return true if you can finish all courses. Otherwise, return false.

 

Example 1:

Input: numCourses = 2, prerequisites = [[1,0]]
Output: true
Explanation: There are a total of 2 courses to take. 
To take course 1 you should have finished course 0. So it is possible.
Example 2:

Input: numCourses = 2, prerequisites = [[1,0],[0,1]]
Output: false
Explanation: There are a total of 2 courses to take. 
To take course 1 you should have finished course 0, and to take course 0 you should also have finished course 1. So it is impossible.

Note:
step 1: add parent node to cycle list
step 2: check if parent node is a edge node or in visited list then delete from dfs and remove form cycle.
step 3: find all child node and check if child node is in cycle list, if found detect cycle and return.
step 4: after adding all child node mark parent node as visited.

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
            
