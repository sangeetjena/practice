"""
https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/description/

You are given an array prices where prices[i] is the price of a given stock on the ith day.

Find the maximum profit you can achieve. You may complete as many transactions as you like (i.e., buy one and sell one share of the stock multiple times) with the following restrictions:

After you sell your stock, you cannot buy stock on the next day (i.e., cooldown one day).
Note: You may not engage in multiple transactions simultaneously (i.e., you must sell the stock before you buy again).

 

Example 1:

Input: prices = [1,2,3,0,2]
Output: 3
Explanation: transactions = [buy, sell, cooldown, buy, sell]
Example 2:

Input: prices = [1]
Output: 0

https://www.youtube.com/watch?v=I7j0F7AHpb8
"""
====== Memoisation =======
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        dp = {}
        def dfs(i, buy):
            if i> len(prices)-1:
                return 0;
            if (i,buy) in dp.keys():
                return dp[(i,buy)]
            if buy:
                # why dfs - prices[i], by putting buying price in -ve, we can add selling price in +ve so finally it will come as difference of selling_price - buying price.
                buyprice = dfs(i+1, not buy) - prices[i]
                notbuy = dfs(i+1, buy)
                dp[(i,buy)] = max(buyprice, notbuy)
            else:
                # why dfs + prices[i], by putting buying price in +ve, finally it will come as difference of selling_price - buying price.
                sellprice = dfs(i+2, not buy) + prices[i]
                notsell = dfs(i+1, buy) #buy is false as it is in else part.
                dp[(i,buy)] = max(sellprice, notsell)
            return dp[(i,buy)]
        return dfs(0,True)

=====Tabulation ======

class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        # Initialize the two initial states 
        # dp[-1] - refers status 1 day ago, dp[-2] refers to status 2 days ago
        # dp[i][0] - represent the profit with having stock in hand
        # dp[i][1] - represent the profit without having stock
        dp = [(-prices[0], 0), (-prices[0], 0)]
        print(dp)
        for i in range(1, len(prices)):
            # To have a stock on hand we have two local choices to make. Those are:
            # 1. Keep the previous stock we have
            # 2. Buy new stock. But we can not buy stock if we buy stock yesterday so we check our profit 
            #     without stok two days ago (dp[2][1]) then we buy the current stock( - prices[i]).
            # Finally we can take the maximum of the two choices.
            keep_last_stock = dp[-1][0]
            buy_new_stock = dp[-2][1] - prices[i]
            with_stock = max(keep_last_stock, buy_new_stock)

            # We also have two choices  to continue without having stock. 
            # 1. keep the previous status without stock (dp[-1][1])
            # 2. sell the previous status with stock (dp[-1][0]). Since we can sell at anytime unlike buying
            # we can take yesterdays stock and sell it( + prices[i])
            
            # Take maximum of the two choices
            prev_empty = dp[-1][1]
            sell_previous_stock = dp[-1][0] + prices[i] 
            no_stock = max(prev_empty, sell_previous_stock)
            # Append current day's status with both states
            dp.append((with_stock, no_stock))

        # Finaly we will have our answer taking the maximum from the states having or not having stock at last.
        return max(dp[-1])
        
