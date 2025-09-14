"""
There are n people and 40 types of hats labeled from 1 to 40.

Given a 2D integer array hats, where hats[i] is a list of all hats preferred by the ith person.

Return the number of ways that n people can wear different hats from each other.

Since the answer may be too large, return it modulo 109 + 7.

 

Example 1:

Input: hats = [[3,4],[4,5],[5]]
Output: 1
Explanation: There is only one way to choose hats given the conditions. 
First person choose hat 3, Second person choose hat 4 and last one hat 5.
Example 2:

Input: hats = [[3,5,1],[3,5]]
Output: 4
Explanation: There are 4 ways to choose hats:
(3,5), (5,3), (1,3) and (1,5)
Example 3:

Input: hats = [[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]]
Output: 24
Explanation: Each person can choose hats labeled from 1 to 4.
Number of Permutations of (1,2,3,4) = 24.


Note: similar to travelling sales man, capture used cap as a bit mask.

"""

class Solution:
    def numberWays(self, hats: List[List[int]]) -> int:
        @lru_cache(None)
        def dfs(visited_mask, pos):
            if pos == len(hats):
                return 1
            total_combination = 0
            for i in hats[pos]:
                # check the current hat is used by other person or not.
                if((1<<i) & (visited_mask))>0:
                    continue
                total_combination +=dfs(visited_mask | 1<<i, pos+1)
            return total_combination
        return dfs(0,0)

        
