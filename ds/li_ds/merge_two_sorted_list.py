"""
You are given two sorted arrays, A and B, where A has a large enough buffer(exactly the required amount) at the end to hold B. Write a method to merge B into A in sorted order.

Example:

Array A of size 10 but with only 5 elements stored: [5, 10, 15, 20, 25]

Array B: [7, 11, 15, 18, 28]

Array A at the end of the solution: [5, 7, 10, 11, 15, 15, 18, 20, 25, 28]
"""
def sort_two_array(arr1, arr2):
    latest = 0
    for i in reversed(range(len(arr2))):
        latest = arr1[-1]
        indj = 0
        for j in reversed(range(len(arr1))):
            indj = j
            if j-1 <0 or arr2[i] > arr1[j-1]:
                break
            arr1[j] = arr1[j-1]
        if (indj != len(arr1)-1 ):
            arr1[indj] = arr2[i]
            arr2[i] = latest
    return arr1 + arr2

print(sort_two_array([5, 10, 15, 20, 25], [7, 11, 15, 18, 28]))


