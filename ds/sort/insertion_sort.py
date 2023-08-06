def insertion_sort(arr):
    print(arr)
    complexity = 0
    for i in range(len(arr)):
        j = i-1
        while j>=0:
            complexity += 1
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                j -= 1
            else:
                break
    print(arr)
    print("complexity - {0}".format(complexity))

insertion_sort([4,5,2,3,1,7,9,8])