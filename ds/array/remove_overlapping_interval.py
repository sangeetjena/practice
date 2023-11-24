"""
there will be n overlapping interval, our job is to remove all overlapping interval with minimum removal.
soln:
sort intervals in the ascending order and then compare overlaping interval and remove the one which is bigger.
"""

def remove_overlap(arr):
    if len(arr) <2:
        return 0
    arr = sorted(arr)
    print(arr)
    p1 = 0
    p2=1
    cnt = 0
    while p1< len(arr) and p2 < len(arr):
        if arr[p2][0] < arr[p1][1]:
            # remove the one which has higher end value.
            if (arr[p2][1]) < (arr[p1][1]):
                p1 = p2
            cnt +=1
            p2+=1
        else:
            p1 = p2
            p2+=1
    return cnt

arr = [(1,4),(3,6),(2,8),(5,9),(7,10)]
print(remove_overlap(arr))
