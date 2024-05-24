"""
https://leetcode.com/problems/shortest-common-supersequence/
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

        
