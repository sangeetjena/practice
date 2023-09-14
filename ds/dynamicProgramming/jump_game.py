def jump_game(arr, i, dest):
    cnt = 0
    jmp = arr[0]
    while i < dest:
        jmp = max([x for x in arr[i+1 : i+jmp+1]])
        i = i + jmp
        cnt += 1
    return cnt +1

arr = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

print(jump_game(arr,0, 9))

arr = [1, 3, 5, 8, 9, 2, 6, 7, 6, 8, 9]

print(jump_game(arr, 0 ,9))