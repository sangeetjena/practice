"""

"""
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        dp = {}
        def dfs(i, buy):
            if i> len(prices)-1:
                return 0;
            if (i,buy) in dp.keys():
                return dp[(i,buy)]
            if buy:
                buyprice = dfs(i+1, not buy) - prices[i]
                cooldownprice = dfs(i+1, buy)
                dp[(i,buy)] = max(buyprice, cooldownprice)
            else:
                sellprice = dfs(i+2, buy) + prices[i]
                cooldownprice = dfs(i+1, not buy) #buy is false as it is in else part.
                dp[(i,buy)] = max(sellprice, cooldownprice)
            return dp[(i,buy)]
        return dfs(0,True)
        
