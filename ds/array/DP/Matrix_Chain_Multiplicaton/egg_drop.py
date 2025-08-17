"""
https://leetcode.com/problems/super-egg-drop/description/

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
                    max_val = max(dp[i-1][l], dp[i][j-l-1])
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
