"""
https://leetcode.com/problems/unique-binary-search-trees/submissions/1268231700/
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
                left = node-1
                right = window-node
                total+= nodes[left] * nodes[right]
            nodes[window] = total
        return nodes[n]
