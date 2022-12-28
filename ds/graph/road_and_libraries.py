#!/bin/python3

import math
import os
import random
import re
import sys
import logging as log

#
# Complete the 'roadsAndLibraries' function below.
#
# The function is expected to return a LONG_INTEGER.
# The function accepts following parameters:
#  1. INTEGER n
#  2. INTEGER c_lib
#  3. INTEGER c_road
#  4. 2D_INTEGER_ARRAY cities
#

""" this a use case of minimum spaning tree (MST)"""
def findcluster(firstcity, cities):
    keys = [firstcity]
    visited = []
    for i in range(0, len(cities)):
        if (len(keys) > len(visited)):
            # visited is used to break the loop
            visited.append(keys[i])
            for y in range(0, len(cities)):
                if cities[y][0] == keys[i] and cities[y][1] not in keys:
                    keys.append(cities[y][1])
                elif cities[y][1] == keys[i] and cities[y][0] not in keys:
                    keys.append(cities[y][0])
        else:
            break
        print("cluster key - {0}".format(keys))
    return keys


def roadsAndLibraries(n, c_lib, c_road, cities):
    # Write your code here
    cost = 0
    visisted_cities = []
    keys = []
    library = []
    clusterkeys = []
    if c_lib < c_road:
        cost = (n) * c_lib
        return cost
    else:
        for city in cities:
            if city[0] in clusterkeys:
                continue
            else:
                library.append(city[0])
                clusterkeys += findcluster(city[0], cities)
                cost += ((len(clusterkeys) - 1) * c_road)
    print(" total road and libraries - :{0} , {1}".format(clusterkeys, library))
    cost += (len(library) * c_lib) + (n - len(clusterkeys)) * c_lib
    return cost


if __name__ == '__main__':

    q = int(input().strip())

    for q_itr in range(q):
        first_multiple_input = input().rstrip().split()

        n = int(first_multiple_input[0])

        m = int(first_multiple_input[1])

        c_lib = int(first_multiple_input[2])

        c_road = int(first_multiple_input[3])

        cities = []

        for _ in range(m):
            cities.append(list(map(int, input().rstrip().split())))

        result = roadsAndLibraries(n, c_lib, c_road, cities)

        print(result)

# explanation:
# 1 - as it is an optimisation problem we have to evaluate cost of library vs cost of road.
# 2 - think it as a cluster problem. first identify howmany cluster/ unconnected cities are there.
# for each cluster we will find minimum road needed and each cluster will take one libray.
#
# corner cases:
#     few cities in the sample would be isolated


# Issues
# optimize code for timeout issue
# less city more road
# 5 9 92 23
# 2 1
# 5 3
# 5 1
# 3 4
# 3 1
# 5 4
# 4 1
# 5 2
# 4 2