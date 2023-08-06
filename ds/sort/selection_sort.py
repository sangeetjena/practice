def selection_sort(arr):
    print(arr)
    complexity = 0
    for i in range(len(arr)):
        for j in range(i+1,len(arr)):
            complexity += 1
            if arr[i] > arr[j]:
                arr[i], arr[j] = arr[j], arr[i]
    print(arr)
    print("complexity  = {0}".format(complexity))

selection_sort([3,6,2,7,9,1])