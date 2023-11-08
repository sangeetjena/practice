"""
merge all overlapping interval to single interval
"""

def merge_overllaping_interval(arr):
    arr = sorted(arr)
    stack = [arr[0]]

    for elem in range(1, len(arr)):
        if stack[-1][1] > arr[elem][0]:
            x = stack[-1]
            del stack[-1]
            stack.append((x[0], arr[elem][1]))
        else:
            stack.append(arr[elem])
    return stack

arr = [(1,4),(3,6),(2,8),(5,9),(9,10)]
print(merge_overllaping_interval(arr))