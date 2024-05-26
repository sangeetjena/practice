"""
https://leetcode.com/problems/unique-binary-search-trees/submissions/1268231700/
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
