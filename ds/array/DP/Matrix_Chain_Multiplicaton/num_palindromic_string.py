"""
https://leetcode.com/problems/palindrome-partitioning/description/



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
