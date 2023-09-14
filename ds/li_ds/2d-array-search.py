def check_if_element_existes(arr, elem):
    for i in range(len(arr)):
        if not (elem >= arr[i][0] or elem <= arr[i][-1]):
            continue
        for j in range(len(arr)):
            if arr[i][j] == elem:
                return True
    return False

arr = [[1,3,5],
       [6,8,9],
       [10,15,30]]
print(check_if_element_existes(arr, 7))