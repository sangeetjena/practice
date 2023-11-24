"""
sub set sum - we need to find no of subsets in an array whose sum = k
ex: [1,5,6,3,4] , sum = 9
out : 3 -> {5,4}, {6,3}, {5,3,1}

approach: for each element we have to decide if we will consider it or not.
if not consider then we will take next element and sum will ramain same
if we will consider then we will move to the next element and we will reduce that value from sum.
"""
def count_sub_set_sum(arr,sum, i):
    # base case
    if sum == 0:
        return 1
    if i<0:
        return 0
    return (count_sub_set_sum(arr,sum, i-1) + count_sub_set_sum(arr,sum-arr[i], i-1))

arr = [1,2,3,5,6,7]
print(count_sub_set_sum(arr, 10,len(arr)-1))

arr = [1,2,1]
print(count_sub_set_sum(arr, 2,len(arr)-1))