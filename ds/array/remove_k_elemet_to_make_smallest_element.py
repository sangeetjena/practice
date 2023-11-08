"""
remove k element fom a number to form a new smallest number possible.
constraint : we can't change the position of integer.   
"""
def remove_k_elements(n, k):
    arr = [x for x in str(n)]
    print(arr)
    k1 = k
    if len(arr)< k:
        return 0
    while k1 > 0:
        l = len(arr)
        i = 0
        while i < len(arr)-2 and k1>0:
            if arr[i]>arr[i+1]:
                del arr[i]
                k1-=1
            else:
                i+=1
        if l == len(arr):
            break
    arr = ''.join(arr)
    return int(arr[:len(arr)-k1])

print(remove_k_elements(34539, 1))

print(remove_k_elements(12345, 1))

print(remove_k_elements(54321, 1))
