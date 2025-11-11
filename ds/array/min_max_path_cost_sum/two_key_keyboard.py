"""
https://leetcode.com/problems/2-keys-keyboard/

There is only one character 'A' on the screen of a notepad. You can perform one of two operations on this notepad for each step:

Copy All: You can copy all the characters present on the screen (a partial copy is not allowed).
Paste: You can paste the characters which are copied last time.
Given an integer n, return the minimum number of operations to get the character 'A' exactly n times on the screen.

 

Example 1:

Input: n = 3
Output: 3
Explanation: Initially, we have one character 'A'.
In step 1, we use Copy All operation.
In step 2, we use Paste operation to get 'AA'.
In step 3, we use Paste operation to get 'AAA'.
Example 2:

Input: n = 1
Output: 0



"""


class Solution:
    def minSteps(self, n: int) -> int:
        dp = {}
        dp[0] = 0
        dp[1] = 0
        dp[2] = 2
        dp[3] = 3
        if n < 4:
            return dp[n]
        for i in range(4, n + 1):
            dp[i] = i
            for j in range(2, n + 1):
                # if n%j is odd then we need n no of steps
                # which we cover in the above step
                if (i % j == 0):
                    # chcking if we can create group of 2, 3, 4, ..n elemnet.
                    # then checking how many step it took to create that group.
                    dp[i] = min(dp[i], dp[int(i / j)] + j)
        return dp[n]
