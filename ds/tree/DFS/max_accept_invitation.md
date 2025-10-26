```
https://leetcode.com/problems/maximum-number-of-accepted-invitations/description/

There are m boys and n girls in a class attending an upcoming party.

You are given an m x n integer matrix grid, where grid[i][j] equals 0 or 1. If grid[i][j] == 1,
 then that means the ith boy can invite the jth girl to the party. A boy can invite at most one girl,
and a girl can accept at most one invitation from a boy.

Return the maximum possible number of accepted invitations.
```
<img width="528" height="465" alt="image" src="https://github.com/user-attachments/assets/49d7076f-bea8-4b7c-8349-6258bc0cabcb" />


``` python
class Solution:
    def maximumInvitations(self, grid: List[List[int]]) -> int:
        m, n = len(grid), len(grid[0])
        ans = 0
        match = [-1] * n
        
        def fn(i): 
            """Look up match for ith boy."""
            for j in range(n):
                if grid[i][j] and not seen[j]: 
                    seen[j] = True
                    if match[j] == -1 or fn(match[j]): 
                        match[j] = i
                        return True 
            return False 
        
        for i in range(m):
            seen = [False] * n
            if fn(i): ans += 1
        return ans 
```
