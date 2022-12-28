
def HighestContiniousSum(lst):
    maxSum=-999
    tempSum=0
    for i in range(0,len(lst)):
        tempSum+=lst[i]
        if tempSum>maxSum:
            maxSum=tempSum
        if (tempSum<0):
            tempSum = 0

    print(maxSum)

HighestContiniousSum([1, 2, -4, 1, 3, -2, 3, -1])