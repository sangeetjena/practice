"""
time complexity: O(NlogN)
logic: devide each element in the array untill single element reached
then merge two array into a temp array
"""


def merge_sort(arr):
    if len(arr) > 1:
        ln = len(arr) // 2
        l = arr[:ln]
        r = arr[ln:]
        merge_sort(l)
        merge_sort(r)
        i = j = k = 0
        while i < len(l) and j < len(r):
            if l[i] < r[j]:
                arr[k] = l[i]
                i += 1
            else:
                arr[k] = r[j]
                j += 1
            k += 1
        while i < len(l):
            arr[k] = l[i]
            i += 1
            k += 1
        while j < len(r):
            arr[k] = r[j]
            j += 1
            k += 1
        return arr


arr = [6, 2, 8, 1, 9, 2, 3, 6]
print(merge_sort(arr))
