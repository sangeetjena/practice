import copy
def is_pallindrom(stck):
    while len(stck)>1:
        a = stck[-1]
        b = stck[0]
        del stck[-1]
        del stck[0]
        if a != b:
            return False
    return True

def longest_palindrom(arr, pals, stck, i):
    print(i)
    for x in range(i, len(arr)):
        stck.append(arr[x])
        print(stck, x)
        if is_pallindrom(copy.deepcopy(stck)):
            pals.append(copy.deepcopy(stck))
        longest_palindrom(arr, pals, stck, x+1)
        del(stck[-1])
    return pals

palindrom = "BBABCBCAB"

print(longest_palindrom(palindrom, [], [], 0))