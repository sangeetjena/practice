def find_num_trangle(arr):
    cnt = 0
    arr.sort()
    print(arr)
    for i in reversed(range(len(arr))):
        j = i-1
        k = 0
        while(k< j):
            if(arr[k] + arr[j] > arr[i]):
                cnt += j-k
                j -=1
            else:
                k+=1
    return cnt
print(find_num_trangle([4, 6, 3, 7]))

