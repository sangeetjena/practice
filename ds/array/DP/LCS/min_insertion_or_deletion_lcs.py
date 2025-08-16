"""
Minimum Deletions & Insertions to Transform a String into another

https://practice.geeksforgeeks.org/problems/minimum-number-of-deletions-and-insertions0209/1/
Note: similar to https://github.com/sangeetjena/practice/blob/master/ds/array/DP/LCS/Edit_distance.py only only remove replace condition.
      calculate the lcs then (i.e: common string) then substreact the lcs length from the two string length.
"""
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        dp = [[0 for _ in range(len(word1)+1)] for _ in range(len(word2)+1)]
        for i in range(1,len(word2)+1):
            for j in range(1,len(word1)+1):
                if word1[j-1] == word2[i-1]:
                    dp[i][j] = 1 + dp[i-1][j-1]
                else:
                    dp[i][j] = max(dp[i][j-1], dp[i-1][j])
        lcs = dp[-1][-1]
        print(lcs)
        max_delete = len(word1) + len(word2) - 2*lcs
        print(max_delete)
        return max_delete

        
