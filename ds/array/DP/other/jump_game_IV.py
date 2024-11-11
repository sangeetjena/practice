"""
https://leetcode.com/problems/jump-game-vii/description/


Note: use simple dfs
"""
class Solution:
    def canReach(self, s: str, minJump: int, maxJump: int) -> bool:
        bfs = []
        if s[0] ==1 or s[-1]==1:
            return False
        print(s[0],s[-1])
        bfs.append(0)
        while bfs:
            i= bfs[-1]
            del bfs[-1]
            if i == len(s)-1:
                return True
            for j in range(i+minJump,min(i+maxJump+1, len(s))):
                if s[j] == '0' :
                    bfs.append(j)
                    # optimisation if already added to bfs then need not re calculate in dfs calls by childs
                    s[j]=1
        return False
