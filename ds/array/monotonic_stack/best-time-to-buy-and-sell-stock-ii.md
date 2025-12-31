'''
https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/description/?envType=study-plan-v2&envId=top-interview-150


You are given an integer array prices where prices[i] is the price of a given stock on the ith day.

On each day, you may decide to buy and/or sell the stock. You can only hold at most one share of the stock at any time. However, you can sell and buy the stock multiple times on the same day, ensuring you never hold more than one share of the stock.

Find and return the maximum profit you can achieve.

Note: monotonic stack pattern, only differnce is need to take min from all stack pop and add that to total profit calculation.


'''

<img width="1440" height="439" alt="image" src="https://github.com/user-attachments/assets/8fca39c4-e416-428b-a478-fd1ccff8dcbc" />


''' python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        total_profit = 0
        stack = []
        for price in prices:
            minstock = price
            while len(stack) and price > stack[-1]:
                minstock =min(minstock, stack[-1])
                del stack[-1]
            total_profit += (price-minstock)
            stack.append(price)
            
        print(total_profit)
        return total_profit
        

'''
