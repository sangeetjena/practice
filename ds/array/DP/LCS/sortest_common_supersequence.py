"""
https://leetcode.com/problems/shortest-common-supersequence/description/

https://www.youtube.com/watch?v=xElxAuBcvsU

Given two strings str1 and str2, return the shortest string that has both str1 and str2 as subsequences. 
If there are multiple valid strings, return any of them.

A string s is a subsequence of string t if deleting some number of characters from t (possibly 0) results in the string s.

Example 1:

Input: str1 = "abac", str2 = "cab"
Output: "cabac"
Explanation: 
str1 = "abac" is a subsequence of "cabac" because we can delete the first "c".
str2 = "cab" is a subsequence of "cabac" because we can delete the last "ac".
The answer provided is the shortest such string that satisfies these properties.
Example 2:

Input: str1 = "aaaaaaaa", str2 = "aaaaaaaa"
Output: "aaaaaaaa"


"""
class Solution:
    def shortestCommonSupersequence(self, str1: str, str2: str) -> str:
        dp = [[0 for _ in range(len(str1)+1)] for _ in range(len(str2)+1)]
        for i in range(1,len(str2)+1):
            for j in range(1,len(str1)+1):
                if str2[i-1] == str1[j-1]:
                    dp[i][j] = 1 + dp[i-1][j-1]
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        # note: for retrun legth of upersequence this much is sufficient  (len(s)-len(lcs)) + (len(s2)-len(lcs)) + len(lcs)
        # to get full string need the below code.
        print(dp)
        i = len(str2)
        j = len(str1)
        fnstr = ""
        while i>=1 and j >= 1:
            print(i,j)
            if str2[i-1] == str1[j-1]:
                fnstr+= str2[i-1]
                i-=1
                j-=1
            else:
                if dp[i][j-1] > dp[i-1][j]:
                    fnstr+= str1[j-1]
                    j=j-1
                else:
                    fnstr+= str2[i-1]
                    i=i-1
            print(fnstr)
        if i==1 and j==1:
            print(fnstr[::-1])
            return fnstr[::-1]
        if i>0:
            fnstr+=str2[:i][::-1]
        else:
            fnstr+=str1[:j][::-1]
        print(fnstr[::-1])
        return fnstr[::-1]

        
