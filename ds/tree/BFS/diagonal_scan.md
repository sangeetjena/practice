```
https://leetcode.com/problems/diagonal-traverse/

Given an m x n matrix mat, return an array of all the elements of the array in a diagonal order.

Note: simply use bfs and for odd scann reverse the array.

```
<img width="485" height="532" alt="image" src="https://github.com/user-attachments/assets/39fe23fc-c951-45de-8cf5-c56509ea5526" />

```python
from collections import deque
class Solution:
    def findDiagonalOrder(self, mat: List[List[int]]) -> List[int]:
        q= deque([(0,0)])
        visited = []
        cnt = 0
        out = [mat[0][0]]
        while len(q)>0:
            l_q = len(q)
            print(l_q)
            tmp = []
            for i in range(l_q):
                x = q.popleft()
                i,j = x
                if j<len(mat[0])-1:
                    if (i,j+1) not in visited:
                        tmp.append((i,j+1))
                        visited.append((i,j+1))
                if i< len(mat)-1:
                    if (i+1, j) not in visited:
                        tmp.append((i+1,j))
                        visited.append((i+1,j))
            q.extend(tmp)
            if cnt%2 != 0:
                tmp= tmp[::-1]
            out+=[mat[i][j] for i,j in tmp]
            cnt+=1
        print(out)
        return out
```
        




        
