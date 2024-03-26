"""
In this problem, we have `m` cakes placed in a row on a baking sheet - eg. Cake 1, Cake 2, Cake 3, ....

- We'd like to decorate each cake either red, green, or blue.
- For each combination of cake and color, we are given the amount of money it costs to decorate that cake with that color.
- A cake cannot be decorated the same color as its neighbor cakes (left and right)
- The goal is to decorate all of the cakes for the minimum total cost.

https://www.youtube.com/watch?v=-w67-4tnH5U
"""
def findMinimumCost(costs):
    for i in range(1, len(costs)):
        for j in range(len(costs[0])):
            # find minimum value in it previous array, except same index position as in current array.
            minCost = 99999
            for k in range(len(costs[0])):
                # dont take same color , i.e same position in the above array.
                if j == k:
                    continue
                if minCost> costs[i-1][k]:
                    minCost = costs[i-1][k]
            costs[i][j] = costs[i][j] + minCost
    print(costs)
    return min(costs[-1])




N = 4
K = 3
costs= [[1, 5, 7], [5, 8, 4], [3, 2, 9], [1, 2, 4]]
print(findMinimumCost(costs))