"""
find number of subset possible in an array whose difference is minimum.
"""
def min_sub_set_diff(arr):
    sum1 = 0
    sum2 = 0
    arr.sort(reverse=True)
    for i in arr:
        if sum1> sum2:
            sum2 += i
        else:
            sum1+=i
    return  abs(sum1 - sum2)

arr = [1,5,6,2,4,3]
print(min_sub_set_diff(arr))