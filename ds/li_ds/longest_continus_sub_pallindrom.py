import copy
def is_pallindrom(arr):
    while len(arr)>1:
        if arr[-1] != arr[0]:
            return False
        del arr[-1]
        del arr[0]
    return True

def longest_cont_sub_pallindrom(arr):
    for i in range(1,len(arr)):
        for j in range(0,i):
            if is_pallindrom(copy.deepcopy(arr[j:j+len(arr)-i])):
                print(arr[j:j+len(arr)-i])
                return
    print("no pallindrom")


palindrom = "BBABABCAB"
print(longest_cont_sub_pallindrom(list(palindrom)))