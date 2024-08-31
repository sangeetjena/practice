"""

https://www.educative.io/courses/grokking-dynamic-programming-a-deep-dive-using-python/solving-the-0-1-knapsack-problem

"""
def find_knapsack(capacity, weights, values, n):
    # Write your code here
    dp = {}
    capacity = total_knapsack(capacity, weights, values, n, dp)
    
    # your code will replace the placeholder return statement below
    return capacity 
def total_knapsack(capacity, weights, values,n, dp):
  if n<=0 or capacity <0:
    return 0
  if (n,capacity) in dp.keys():
    return dp[(n,capacity)]
  if weights[n-1] <=capacity:
    dp[(n,capacity)] = max(values[n-1]+total_knapsack(capacity-weights[n-1],weights,values,n-1,dp), 
                          total_knapsack(capacity,weights,values,n-1,dp))
  else:
    dp[(n,capacity)] = total_knapsack(capacity,weights,values,n-1,dp)
  return dp[(n,capacity)]



find_nkapsack(6 , [1,2,3,5] , [1,5,4,8] , 4)
