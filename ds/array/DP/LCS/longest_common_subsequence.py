"""
https://leetcode.com/problems/longest-common-subsequence/description/

Q:  1143. Longest Common Subsequence
Given two strings text1 and text2, return the length of their longest common subsequence. If there is no common subsequence, return 0.

A subsequence of a string is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.

For example, "ace" is a subsequence of "abcde".
A common subsequence of two strings is a subsequence that is common to both strings.

Example 1:

Input: text1 = "abcde", text2 = "ace"
Output: 3
Explanation: The longest common subsequence is "ace" and its length is 3.
"""
class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        dp = [[0 for i in range(len(text1) + 1)] for j in range(len(text2) +1)]
        for i in range(1, len(text1) + 1):
            for j in range(1, len(text2) + 1):
                if text1[i-1] == text2[j-1]:
                    dp[j][i] = 1+ dp[j-1][i-1]
                else:
                    dp[j][i] = max(dp[j-1][i] , dp[j][i-1])
        return dp[-1][-1]
        

# memoisatin 

class Solution:
    def dfs(self, s1, s2, i, j):
        if i > len(s1)-1 or j > len(s2)-1:
            return 0
        if (i, j) in self.dp:
            return self.dp[(i, j)]
        res = 0
        if s1[i] == s2[j]:
            res = 1 + self.dfs(s1, s2, i+1, j+1)
        take1 = self.dfs(s1,s2, i+1, j)
        take2 = self.dfs(s1, s2, i, j+1) 
        res = max(res, take1, take2)
        self.dp[(i,j)] = res
        return res

    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        self.dp = defaultdict(int)
        res = self.dfs(text1, text2, 0, 0)
        return res
