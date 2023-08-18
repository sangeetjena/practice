def find_n_largest_element(arr, n):
    p_queue = [0 for i in range(0,n)]
    for x in arr:
        for y in range(0,n):
            if x> p_queue[y]:
                if y<n:
                    p_queue[y+1:] = p_queue[y:n-1]
                p_queue[y] = x
                break
    print(p_queue)

arr = [1,2,3,4,5]
find_n_largest_element(arr, 3)