"""
https://www.geeksforgeeks.org/longest-repeating-subsequence/

Input: s= "abc"
Output: 0
Explanation: There is no repeating subsequence

Input: s= "aab"
Output: 1
Explanation: The two subsequence are 'a'(0th index) and 'a'(1th index). Note that 'b' cannot be considered as part of subsequence as it would be at same index in both. 


Note: same as LCS with extra condition [ arr[i] != arr[j] ]
Clue: in a string while we are finding subsequence if we are eleminating same index position then we will find another sub sequence.
"""
#User function Template for python3

class Solution:
	def LongestRepeatingSubsequence(self, s):
		# Code here
		dp = [[0 for _ in range(len(s)+1)] for _ in range(len(s)+1)]
		for i in range(1, len(s)+1):
		    for j in range(1, len(s)+1):
		        if i<j:
		            if s[i-1] == s[j-1]:
		                dp[i][j] = 1 + dp[i-1][j-1]
		            else:
		                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            # for same index position we need not to do any computation. only take the max value from up and down location of the dp
		        else:
		            dp[i][j] = max(dp[i-1][j], dp[i][j-1])
		return dp[-1][-1]
