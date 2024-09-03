"""
https://www.geeksforgeeks.org/count-ofdifferent-ways-express-n-sum-1-3-4/

Note: similar to climbing stair

"""
def countWays(n): 
  
    DP = [0 for i in range(0, n + 1)] 
      
    # base cases 
    DP[0] = DP[1] = DP[2] = 1
    DP[3] = 2
  
    # Iterate for all values from 4 to n 
    for i in range(4, n + 1): 
        DP[i] = DP[i - 1] + DP[i - 3] + DP[i - 4] 
      
    return DP[n] 
  
      
# Driver code  
n = 10
print (countWays(n)) 
