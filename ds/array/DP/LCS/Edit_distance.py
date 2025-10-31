"""
https://leetcode.com/problems/edit-distance/description/

https://www.youtube.com/watch?v=XYi2-LPrwm4


Given two strings word1 and word2, return the minimum number of operations required to convert word1 to word2.
You have the following three operations permitted on a word:

Insert a character
Delete a character
Replace a character
 
Example 1:
Input: word1 = "horse", word2 = "ros"
Output: 3
Explanation: 
horse -> rorse (replace 'h' with 'r')
rorse -> rose (remove 'r')
rose -> ros (remove 'e')
Example 2:

Input: word1 = "intention", word2 = "execution"
Output: 5
Explanation: 
intention -> inention (remove 't')
inention -> enention (replace 'i' with 'e')
enention -> exention (replace 'n' with 'x')
exention -> exection (replace 'n' with 'c')
exection -> execution (insert 'u')

Note: similar to the LCS
only difference is if match then don't need to increase just check if precious elemnts had anything to relace, delete . i.e dp[i-1][j-1]
and if not match then check digonal, up, and down to check if any replace , delete or insert. 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])

"""

class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        dp = [[float("inf") for _ in range(len(word1)+1)] for _ in range(len(word2)+1) ]
        for i in range(len(word2)+1):
            for j in range(len(word1)+1):
                if i==0 or j==0:
                    dp[i][j] = max(i,j)
                    continue
                if word2[i-1] == word1[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    # if not match then option 1: delete or insert in word1 or word2 i.e (dp[i-1][j] or dp[i][j-1])
                    # or replace charector between word1 and word2, if relaced i.e 1 operation and then bothe the word became same so check what was max operation to the previous index i.e [i-1][j-1]
                    dp[i][j] = 1 + min(
                    dp(i - 1, j),      # Delete
                    dp(i, j - 1),      # Insert
                    dp(i - 1, j - 1)   # Replace
                )
        lcs = dp[-1][-1]
        print(dp)
        return lcs
        
