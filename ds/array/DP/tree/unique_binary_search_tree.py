"""
https://leetcode.com/problems/unique-binary-search-trees/submissions/1268231700/

Given an integer n, return the number of structurally unique BST's (binary search trees) which has exactly n nodes of unique values from 1 to n.

 

Example 1:


Input: n = 3
Output: 5
Example 2:

Input: n = 1
Output: 1
 

Constraints:

1 <= n <= 19

Note: DP problem
here value of nodes doesnot matter, it depends if you take a value as root how many elements are there in its left and its right.
that will decide how many tree can be formed.
1st take small window and check if we will take one value in the windlow how many tree can beformed, store that to the dp 
then increase the window size and reuse already calculated value for its earlier window.
"""
class Solution:
    def numTrees(self, n: int) -> int:
        nodes = [1] * (n+1)
        
        for window in range(2, n+1):
            total = 0
            for node in range(1, window+1):
                # for ex 4 element, if root is at 0 then left has 0 node and right has 4-0=4
                # if root is at 1 then left has 1 node and right has 4-1 = 3 mode...
                left = node-1 
                right = window-node
                total+= nodes[left] * nodes[right]
            nodes[window] = total
        return nodes[n]
