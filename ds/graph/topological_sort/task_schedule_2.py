"""
https://leetcode.com/problems/course-schedule-ii/

There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1. You are given an array prerequisites where prerequisites[i] = [ai, bi] indicates that you must take course bi first if you want to take course ai.

For example, the pair [0, 1], indicates that to take course 0 you have to first take course 1.
Return the ordering of courses you should take to finish all courses. If there are many valid answers, return any of them. If it is impossible to finish all courses, return an empty array.

 

Example 1:

Input: numCourses = 2, prerequisites = [[1,0]]
Output: [0,1]
Explanation: There are a total of 2 courses to take. To take course 1 you should have finished course 0. So the correct course order is [0,1].
Example 2:

Input: numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]]
Output: [0,2,1,3]
Explanation: There are a total of 4 courses to take. To take course 3 you should have finished both courses 1 and 2. Both courses 1 and 2 should be taken after you finished course 0.
So one correct course order is [0,1,2,3]. Another correct ordering is [0,2,1,3].
Example 3:

Input: numCourses = 1, prerequisites = []
Output: [0]


Note:
step 1: add parent node to cycle list
step 2: check if parent node is a edge node or in visited list then delete from dfs and remove form cycle, add node to output list.
step 3: find all child node and check if child node is in cycle list, if found detect cycle and return.
step 4: after adding all child node mark parent node as visited.

"""
class Solution:
    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:
        dct = {}
        # create adjacency hash map
        for p, c in prerequisites:
            if p in dct.keys():
                dct[p].append(c)
            else:
                dct[p] = [c]
        out , visited , cycle , dfs = [],[],set(),[]
        for node in dct.keys():
            if node in visited:
                continue
            dfs.append(node)
            while len(dfs) >0:
                k = dfs[-1]
                # step 1: add parent node to the cycle list sothat i can check if any child node is creating cycle.
                # i.e child node is already in cycle list
                cycle.add(k)
                # step 2a: check if node is already visited or a leaf node , then delete from cycle. and remove from dfs
                if (k not in dct.keys()) or (k in visited):
                    if k not in out:
                        out.append(k)
                    del dfs[-1]
                    cycle.remove(k)
                else:
                # step 2b: if node is not already visited and not leaf node then see all its child node is not part of cycle else add to dfs
                    for i in dct[k]:
                        if i in cycle:
                            return []
                        dfs.append(i)
                #step 3: once all child added to dfs mark parent node as visited.
                visited.append(k)
            cycle = set()
        for i in reversed(range(numCourses)):
            if i not in out:
                out = [i] + out
        return out
        
