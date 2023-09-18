# Given an array arr[] consisting of N positive integers representing the ratings of N children,
# the task is to find the minimum number of candies required for distributing to N children such that
# every child gets at least one candy and the children having the higher rating get more candies than its neighbours.
#
# Input: arr[] = {1, 0, 2}
# Output: 5
# Explanation:
# Consider the distribution of candies as {2, 1, 2} that satisfy the given conditions. Therefore, the sum of candies is 2 + 1 + 2 = 5, which is the minimum required candies.

def find_no_of_candies(arr):
    l_candy = [1 for i in range(len(arr))]
    r_candy = [1 for i in range(len(arr))]
    total_candy = 0
    # left side max candy
    for i in range(len(arr)-1):
        if arr[i+1] > arr[i]:
            l_candy[i+1] = l_candy[i] + 1
    # right side max candy
    for i  in reversed(range(1, len(arr))):
        if arr[i-1] > arr[i]:
            r_candy[i-1] = r_candy[i] + 1
    # total candy
    for i in range(len(l_candy)):
        total_candy = total_candy + max(l_candy[i], r_candy[i])
    return total_candy

print(find_no_of_candies([4,3,5,6,2]))

print(find_no_of_candies([1,0,2]))

print(find_no_of_candies([1, 2, 2]))
