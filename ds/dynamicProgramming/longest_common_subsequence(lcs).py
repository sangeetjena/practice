"""
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
def LCS(arr1, arr2):
    dp = [[0 for i in range(len(arr1) + 1)] for j in range(len(arr2) +1)]
    for i in range(1, len(arr1) + 1):
        for j in range(1, len(arr2) + 1):
            if arr1[i-1] == arr2[j-1]:
                dp[j][i] = 1+ dp[j-1][i-1]
            else:
                dp[j][i] = max(dp[j-1][i] , dp[j][i-1])
    return dp[-1][-1]

print(LCS("abcde", "ace"))
print(LCS("ace", "abcde"))
print(LCS("accenture", "actep"))
