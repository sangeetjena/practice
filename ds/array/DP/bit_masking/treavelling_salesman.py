"""
https://www.geeksforgeeks.org/dsa/travelling-salesman-problem-using-dynamic-programming/

Given a 2d matrix cost[][] of size n where cost[i][j] denotes the cost of moving from city i to city j. The task is to complete a tour from city 0 (0-based index) to all other cities such that we visit each city exactly once and then at the end come back to city 0 at minimum cost.

Note the difference between Hamiltonian Cycle and TSP. The Hamiltonian cycle problem is to find if there exists a tour that visits every city exactly once. Here we know that Hamiltonian Tour exists (because the graph is complete) and in fact, many such tours exist, the problem is to find a minimum weight Hamiltonian Cycle. 

Examples:

Input: cost[][] = [[0, 111], [112, 0]]
Output: 223
Explanation: We can visit 0->1->0 and cost = 111 + 112 = 223.

Input: cost[][] = [[0, 1000, 5000], [5000, 0, 1000], [1000, 5000, 0]]
Output: 3000
Explanation: We can visit 0->1->2->0 and cost = 1000 + 1000 + 1000 = 3000.

Note: 
1- why it didn't solved using graph (disktra , etc) ? because here we need to take all the points and find all possible combination and from that we have to take the min value
as we are finding all possible combination, it is a dp problem. 
2- why we chose bit making , not a array to store visited or not ?
    a1: operation in array would need a search with O(n) complexith. but in bit mask it is artihmetic operation
    a2: storage will be huse in comparision to a number (each bit represent value is set or not)


"""
# Python program to find the shortest possible route
# that visits every city exactly once and returns to
# the starting point using memoization and bitmasking

import sys
def totalCost(mask, pos, n, cost):
  
    # Base case: if all cities are visited, return the
    # cost to return to the starting city (0)
    # if mask ex: 111 -> 7 , then (1 << n) - 1 means (1000 i.e 8) -> 8-1 = 7 (go to the next number -1 = current value i.e mask value.
    if mask == (1 << n) - 1:
        return cost[pos][0]

    ans = sys.maxsize   

    # Try visiting every city that has not been visited yet
    for i in range(n):
        if (mask & (1 << i)) == 0: 
  
            # If city i is not visited, visit it and 
             #  update the mask
            ans = min(ans, cost[pos][i] +
                      totalCost(mask | (1 << i), i, n, cost))

    return ans
 

def tsp(cost):
    n = len(cost)
    
    # Start from city 0, and only city 0 is visited 
    # initially (mask = 1)
    return totalCost(1, 0, n, cost)
 
if __name__ == "__main__":
    
    cost = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]
    ]

    result = tsp(cost)
    print(result)
