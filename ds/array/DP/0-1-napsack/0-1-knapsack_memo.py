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

# def find_knapsack(capacity, weights, values, n):
#     dp = [[-1 for i in range(capacity + 1)] for j in range(n + 1)]
#     return find_knapsack_value(capacity, weights, values, n, dp)

# def find_knapsack_value(capacity, weights, values, n, dp):
#     # Base case
#     if n == 0 or capacity == 0:
#         return 0
    
#     #If we have solved it earlier, then return the result from memory
#     if dp[n][capacity] != -1:
#         return dp[n][capacity]
 
#     #Otherwise, we solve it for the new combination and save the results in the memory
#     if weights[n-1] <= capacity:
#         dp[n][capacity] = max(
#             values[n-1] + find_knapsack_value(capacity-weights[n-1], weights, values, n-1, dp),
#             find_knapsack_value(capacity, weights, values, n-1, dp)
#             )
#         return dp[n][capacity]

#     dp[n][capacity] = find_knapsack_value(capacity, weights, values, n-1, dp)
#     return dp[n][capacity] 

find_nkapsack(6 , [1,2,3,5] , [1,5,4,8] , 4)
