"""
Minimum Deletions & Insertions to Transform a String into another

https://practice.geeksforgeeks.org/problems/minimum-number-of-deletions-and-insertions0209/1/

Given two strings s1 and s2. The task is to remove or insert the minimum number of characters from/in s1 to transform it into s2. 
It could be possible that the same character needs to be removed from one point of s1 and inserted into another point.

Example:
Input: s1 = "heap", s2 = "pea"
Output: 3
Explanation: 'p' and 'h' deleted from heap. Then, 'p' is inserted at the beginning.

Input : s1 = "geeksforgeeks", s2 = "geeks"
Output: 8
Explanation: 8 deletions, i.e. remove all characters of the string "forgeeks".

Note: similar to https://github.com/sangeetjena/practice/blob/master/ds/array/DP/LCS/Edit_distance.py only only remove replace condition.
      delete or insert: insert is as good as delete.
      calculate the lcs then (i.e: common string) then substreact the lcs length from the two string length.
      s1-lcs + s2-lcs => s1+s2-2lcs
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

        
