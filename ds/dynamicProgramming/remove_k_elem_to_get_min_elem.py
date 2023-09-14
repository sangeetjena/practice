"""
remove k element from a string to get minimum element.
ex: 1456083 k=3
out: 1403
Note: we can't jumble the sequence.
"""
def remove_k_elem(arr,k):
    for i in range(k):
        swap = 0
        for j in range(len(arr)-2):
            if arr[j] > arr[j+1]:
                arr[j:] = arr[j+1:]
            swap =1
        if swap ==0 or len(arr) == k:
            return arr[0:k]
    return arr[0:k]

print(remove_k_elem([1,4,5,6,0,8,3], 4))