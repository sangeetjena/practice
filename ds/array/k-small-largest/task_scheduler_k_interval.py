"""
https://leetcode.com/problems/task-scheduler/description/

You are given an array of CPU tasks, each represented by letters A to Z, and a cooling time, n. Each cycle or interval allows the completion of one task. Tasks can be completed in any order, but there's a constraint: identical tasks must be separated by at least n intervals due to cooling time.

​Return the minimum number of intervals required to complete all tasks.

 

Example 1:

Input: tasks = ["A","A","A","B","B","B"], n = 2

Output: 8

Explanation: A possible sequence is: A -> B -> idle -> A -> B -> idle -> A -> B.

After completing task A, you must wait two cycles before doing A again. The same applies to task B. In the 3rd interval, neither A nor B can be done, so you idle. By the 4th cycle, you can do A again as 2 intervals have passed.



"""
class Solution:
    def leastInterval(self, tasks: List[str], n: int) -> int:
        import heapq
        dct = {}
        for x in tasks:
            if x in dct.keys():
                dct[x]+=1
            else:
                dct[x] = 1
        q = []
        lst = [(-dct[val], val) for val in dct.keys()]
        heapq.heapify(lst)
        i =0
        while len(lst) or len(q):
            cnt=0
            val = 0
            if len(lst)>0:
                cnt, val = heapq.heappop(lst)
                cnt+=1
            i+=1
            
            if cnt<0:
                q.append((cnt,val, i ))
            if len(q)>0 and (i-q[0][2])>=n:
                heapq.heappush(lst, (q[0][0], q[0][1]))
                del q[0]
        return i
        
