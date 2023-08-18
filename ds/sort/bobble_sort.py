# time complexity = O(n^2)
# difference between insertion sort and bobble sort is
# in insertion sort loop goes from (j to i-1)
# where as in bobble sort loops froes from j to (n-i-1)
def bubble_sort(arr):
    for i in range(0, len(arr)):
        swap = False
        for j in range(0, len(arr)-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swap = True
        if swap == False:
            break
    print(arr)

arr = [2,5,3,9,4,2,1]
bubble_sort(arr)
