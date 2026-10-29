"""
https://leetcode.com/problems/super-egg-drop/description/

https://www.youtube.com/watch?v=UvksR0hR9nA

You are given k identical eggs and you have access to a building with n floors labeled from 1 to n.

You know that there exists a floor f where 0 <= f <= n such that any egg dropped at a floor higher than f will break, and any egg dropped at or below floor f will not break.

Each move, you may take an unbroken egg and drop it from any floor x (where 1 <= x <= n). If the egg breaks, you can no longer use it. However, if the egg does not break, you may reuse it in future moves.

Return the minimum number of moves that you need to determine with certainty what the value of f is.

 

Example 1:

Input: k = 1, n = 2
Output: 2
Explanation: 
Drop the egg from floor 1. If it breaks, we know that f = 0.
Otherwise, drop the egg from floor 2. If it breaks, we know that f = 1.
If it does not break, then we know f = 2.
Hence, we need at minimum 2 moves to determine with certainty what the value of f is.
Example 2:

Input: k = 2, n = 6
Output: 3
Example 3:

Input: k = 3, n = 14
Output: 4
 

"""
# memoisation 
class Solution:
    def dfs(self, s, e, egg):
        # - s > e: no floors remain → 0 drops.
        # - s == e: one floor remains → 1 drop.
        # - egg == 0 with floors remaining: impossible → infinity.
        # - egg == 1: test sequentially → e - s + 1 drops.
        # base case
        if s > e:
            return 0
        if egg == 0:
            return float("inf")
        if s == e:
            return 1
        if egg == 1:
            return e - s + 1

        # memoisation
        state = (s, e, egg)
        if state in self.dp:
            return self.dp[state]

        minval = float("inf")

        # recurssion logic
        for floor in range(s, e + 1):
            egg_break = self.dfs(s, floor - 1, egg - 1)
            egg_not_break = self.dfs(floor + 1, e, egg)

            worst_case = 1 + max(egg_break, egg_not_break)
            minval = min(minval, worst_case)

        self.dp[state] = minval
        return minval

    def superEggDrop(self, k: int, n: int) -> int:
        self.dp = {}
        return self.dfs(1, n, k)



# Tabulation technique
class Solution:
    def superEggDrop(self, k: int, n: int) -> int:
        dp = [[0 for _ in range(n+1)] for _ in range(k+1)]
        for i in range(1,k+1):
            for j in range(1,n+1):
                #base case:
                    # with 1 egg n time we have to try
                    # with 0,1 floor onely 1 time we can try.
                if i == 1:
                    dp[i][j] = j
                    continue
                if j == 1:
                    dp[i][j] = 1
                    continue
                min_val_perfloor = 9999999
                for l in range(0,j):
                    # at l-th floot if we will throw an egg there would be two cases - 1- egg break or 2 -  egg service.
                    # if egg service then the critical floor remains to check is j-k and eggs will remain as it is i.e i
                    # if egg break then the critical floor would bve bellow l floor , and eggs remain = i-1 and floor remain as l-q
                    max_val = max(dp[i-1][l], dp[i][j-l-1])
                    # after comparing from all the floor, find what is the min attempt it took comparing all the floors
                    min_val_perfloor = min(min_val_perfloor, max_val)
                dp[i][j] = 1 + min_val_perfloor
        return dp[-1][-1]
                
===============




OTher approach:

class Solution:
    def superEggDrop(self, k: int, n: int) -> int:
        dp = [[0 for _ in range(k+1)] for _ in range(n+1)]
        floor = 0
        while dp[floor][k] < n:
            floor += 1
            for i in range(1, k+1):
                dp[floor][i] = 1 + dp[floor-1][i] + dp[floor-1][i-1]
        return floor
