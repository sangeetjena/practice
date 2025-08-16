"""
https://www.geeksforgeeks.org/longest-repeating-subsequence/

Note: same as LCS with extra condition [ arr[i] != arr[j] ]
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
