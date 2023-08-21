import copy
def is_trangle(sub_arr):
    a = sub_arr[0]
    b = sub_arr[1]
    c = sub_arr[2]
    if a + b <= c:
        return False
    if a + c <= b:
        return False
    if b + c <= a:
        return False
    return True
def num_trangles(arr, sub_trang, tranges, x):
    for i in range(x, len(arr)):
        if len(sub_trang)>3:
            return
        sub_trang.append(arr[i])
        if len(sub_trang) == 3 and is_trangle(sub_trang):
            tranges.append(copy.deepcopy(sub_trang))
        num_trangles(arr,sub_trang, tranges, i +1)
        del sub_trang[-1]
    return tranges

trang = [10, 21, 22, 100, 101, 200, 300]
print(num_trangles(trang, [], [], 0))
