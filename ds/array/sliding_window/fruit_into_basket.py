"""
https://leetcode.com/problems/fruit-into-baskets/description/

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
