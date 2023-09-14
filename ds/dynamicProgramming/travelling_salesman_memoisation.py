import sys

"""
this is similar to find all possible sum in a list problem.
use a stack to accumulate all possible combination from one point in recurssion.
"""
import copy
def travelling_sales_man(arr, weight, stck, ind):
    for i in range(len(arr)):
        if i in stck or arr[ind][i] == 0:
            continue
        print(i, ind, weight[ind] + arr[ind][i])
        stck.append(i)
        weight[i] = weight[ind] + arr[ind][i]
        (max(travelling_sales_man(arr,copy.deepcopy(weight), copy.deepcopy(stck), i )))
        weight[i] = 0
        del stck[-1]
    print("stack ",stck)
    print(weight)
    return weight

dist = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]

print(travelling_sales_man(dist, [0 for i in range(len(dist))], [0], 0))