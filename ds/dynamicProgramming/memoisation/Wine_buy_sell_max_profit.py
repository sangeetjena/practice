"""
Given n wines in a row, with integers denoting the cost of each wine respectively.
Each year you can sale the first or the last wine in a row.
However, the price of wines increases over time.
Let the initial profits from the wines be P1, P2, P3…Pn.
In the Yth year, the profit from the ith wine will be Y*Pi.
For each year, your task is to print “beg” or “end” denoting whether first or last wine should be sold.
 Also, calculate the maximum profit from all the wines.

 Input: Price of wines: 2 4 6 2 5
Output: beg end end beg beg
         64
Explanation :
"""

def max_profit(arr, s,e, y,dp):
    if dp[s][e] != -1:
        return dp[s][e]
    if (s >= e):
        return arr[s] * y
    left = (arr[s] * y) + max_profit(arr, s+1,e, y+1, dp)
    right = (arr[e] * y) + max_profit(arr, s, e - 1, y+1, dp)
    dp[s][e] = max(left, right)
    return dp[s][e]

arr = [2,4,6,2,5]
dp = [[-1 for i in range(len(arr))] for x in range(len(arr))]
print(max_profit(arr, 0, len(arr)-1, 1, dp))
