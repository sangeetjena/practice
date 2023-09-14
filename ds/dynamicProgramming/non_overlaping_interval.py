"""
there is a time seties of interval. find how many interval to remove to make all set as non overlapping interval
"""
def remove_overlaping_time_series(arr: []):
    arr.sort(reverse=False)
    stck = []
    cnt = 0
    for l,h in  arr:
        if len(stck) == 0:
            stck.append((l,h))
            continue
        l1, h1 = stck[-1]
        print((l,h), (l1,h1))
        if h1 > l:
            cnt += 1
            continue
        else:
            stck.append((l,h))
    print(stck)
    return cnt

print(remove_overlaping_time_series([(0,6),(2,6),(4,6),(6,8)]))
