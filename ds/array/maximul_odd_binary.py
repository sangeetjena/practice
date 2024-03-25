def max_odd_bin(n):
    ons = 0
    length = 0
    while n!=0:
        if n%2 !=0:
            ons += 1
        n = n//2
        length += 1
    arr = [0 for x in range(0,length)]
    arr[-1] = 1
    for i in range(0, ons-1):
        arr[i] = 1
    return str(arr)

print(max_odd_bin(2))

