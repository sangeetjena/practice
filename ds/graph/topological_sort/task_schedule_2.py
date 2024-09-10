"""
https://leetcode.com/problems/course-schedule-ii/

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
        
