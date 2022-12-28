#!/bin/python3

import math
import os
import random
import re
import sys


"""
There will be two arrays of integers. Determine all integers that satisfy the following two conditions:
The elements of the first array are all factors of the integer being considered
The integer being considered is a factor of all elements of the second array
These numbers are referred to as being between the two arrays. Determine how many such numbers exist.
Example 
 

There are two numbers between the arrays:  and . 
, ,  and  for the first value. 
,  and ,  for the second value. Return .
"""

"""
solution : 
assumption : two array is sorted
catch over here is that for gcd in array a, the elements could be between the 
largest element of a[-1] and smallest element of b[0] -> gcd[]

then in order to find the common factor of b
we need to find elements of gcd in array b , b[0] % gcd[i..]
"""

def getTotalX(a, b):
    # Write your code here
    start = a[-1]
    end = b[0]
    gcd = []
    for i in range(start, end + 1):
        allin = True
        for j in a:
            if i % j != 0:
                allin = False
        if (allin == True):
            gcd.append(i)
    lcd = []
    for i in gcd:
        allin = True
        for y in b:
            if y % i != 0:
                allin = False
                break
        if allin == True:
            lcd.append(i)
    return len(lcd)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    m = int(first_multiple_input[1])

    arr = list(map(int, input().rstrip().split()))

    brr = list(map(int, input().rstrip().split()))

    total = getTotalX(arr, brr)

    fptr.write(str(total) + '\n')

    fptr.close()
