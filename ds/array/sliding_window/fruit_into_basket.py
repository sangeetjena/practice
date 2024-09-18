"""
https://leetcode.com/problems/fruit-into-baskets/description/

You are visiting a farm that has a single row of fruit trees arranged from left to right. The trees are represented by an integer array fruits where fruits[i] is the type of fruit the ith tree produces.

You want to collect as much fruit as possible. However, the owner has some strict rules that you must follow:

You only have two baskets, and each basket can only hold a single type of fruit. There is no limit on the amount of fruit each basket can hold.
Starting from any tree of your choice, you must pick exactly one fruit from every tree (including the start tree) while moving to the right. The picked fruits must fit in one of your baskets.
Once you reach a tree with fruit that cannot fit in your baskets, you must stop.
Given the integer array fruits, return the maximum number of fruits you can pick.

 

Example 1:

Input: fruits = [1,2,1]
Output: 3
Explanation: We can pick from all 3 trees.


NOte: as we have two basket in this problem so we can have max two type of tree in the max window. so this problem is find max window with at most two kind of tree.


"""
class Solution:
    def totalFruit(self, fruits: List[int]) -> int:
        dp = {}
        window, maxtree=0,0 
        start, end = 0,0
        while end < len(fruits):
            if fruits[end] not in dp.keys():
                dp[fruits[end]] = 1
            else:
                dp[fruits[end]]+=1
            window+=1
            while len(dp.keys())>2:
                dp[fruits[start]] -=1
                window-=1
                if dp[fruits[start]] == 0:
                    del dp[fruits[start]]
                start+=1
            maxtree = max(maxtree, window)
            end+=1
        return maxtree
