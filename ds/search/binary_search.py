"""
time complexity : O(logN)
limitation: array need to be sorted before we start binary search

"""

def binary_search(arr, element):
    lft = 0
    r = len(arr) - 1
    while lft <= r:
        mid = ((r + lft) // 2)
        print(mid)
        print(lft,r)
        if arr[mid] == element:
            return 1
        elif element > arr[mid]:
            lft = mid + 1
        else:
            r = mid - 1
    return 0

arr = [0,2,3,5,6,7,9]
print(binary_search(arr,4))

